/**
 * @file abstraction.c
 * @author G.J.J. van den Burg
 * @date 2019-03-04
 * @brief Code for speeding up the pattern score computation
 *
 * Copyright (c) The Alan Turing Institute.
 * See the LICENSE file for licensing information.
 *
*/

#define MODULE_VERSION "1.0"

#include <stdbool.h>

#include "Python.h"

static int _set_char(const char *name, Py_UCS4 *target, PyObject *src, Py_UCS4 dflt)
{
	if (src == NULL) {
		*target = dflt;
		return 0;
	}
	*target = '\0';
	if (src != Py_None) {
		Py_ssize_t len;
		if (!PyUnicode_Check(src)) {
			PyErr_Format(PyExc_TypeError,
					"\"%s\" must be string, not %.200s", name,
					src->ob_type->tp_name);
			return -1;
		}
		len = PyUnicode_GetLength(src);
		if (len > 1) {
			PyErr_Format(PyExc_TypeError,
					"\"%s\" must be a 1-character string",
					name);
			return -1;
		}
		/* PyUnicode_READY() is called in PyUnicode_GetLength() */
		if (len > 0)
			*target = PyUnicode_READ_CHAR(src, 0);
	}
	return 0;
}


PyObject *base_abstraction(PyObject *self,  PyObject *args)
{
	int kind;
	void *data;
	Py_UCS4 s, delimiter, quotechar, escapechar;
	char *stack = NULL;
	size_t i, len = 0;
	size_t stack_size_new, stack_size = 4096;

	PyObject *S = NULL,
		 *delimiter_obj = NULL,
		 *quotechar_obj = NULL,
		 *escapechar_obj = NULL;

	if (!PyArg_ParseTuple(args, "OOOO", &S, &delimiter_obj, &quotechar_obj,
				&escapechar_obj)) {
		printf("Error parsing arguments.\n");
		return NULL;
	}

	if (_set_char("delimiter", &delimiter, delimiter_obj, ',') < 0)
		return NULL;
	if (_set_char("quotechar", &quotechar, quotechar_obj, 0) < 0)
		return NULL;
	if (_set_char("escapechar", &escapechar, escapechar_obj, 0) < 0)
		return NULL;

	if (PyUnicode_READY(S) == -1) {
		printf("Unicode object not ready.\n");
		return NULL;
	}
	kind = PyUnicode_KIND(S);
	data = PyUnicode_DATA(S);

	stack = malloc(sizeof(char) * stack_size);
	if (stack == NULL)
		return NULL;
	for (i=0; i<stack_size; i++) stack[i] = '\0';

	int escape_next = 0;
	for (i=0; i<(size_t)PyUnicode_GET_LENGTH(S); i++) {
		s = PyUnicode_READ(kind, data, i);
		if (s == '\r' || s == '\n') {
			if (stack[len-1] != 'R')
				stack[len++] = 'R';
		} else if (s == delimiter) {
			if (escape_next) {
				stack[len++] = 'C';
				escape_next = 0;
			} else
				stack[len++] = 'D';
		} else if (s == quotechar) {
			if (escape_next) {
				stack[len++] = 'C';
				escape_next = 0;
			} else
				stack[len++] = 'Q';
		} else if (s == escapechar) {
			if (escape_next) {
				if (stack[len-1] != 'C')
					stack[len++] = 'C';
				escape_next = 0;
			} else
				escape_next = 1;
		} else {
			if (escape_next)
				escape_next = 0;
			if (len == 0 || stack[len-1] != 'C')
				stack[len++] = 'C';
		}
		if (len == stack_size) {
			stack_size_new = 2 * stack_size;
			char *stack_new = stack;
			stack_new = realloc(stack_new, sizeof(char)*stack_size_new);
			if (stack_new == NULL) {
				PyErr_NoMemory();
				return 0;
			}
			stack = stack_new;
			stack_size = stack_size_new;
		}
	}

	PyObject *stack_obj = PyUnicode_FromStringAndSize(stack, (Py_ssize_t)len);
	if (stack_obj == NULL)
		goto err;
	Py_INCREF(stack_obj);

err:
	free(stack);
	return stack_obj;
}

PyObject *c_merge_with_quotechar(PyObject *self, PyObject *args)
{
	int kind;
	void *data;

	bool in_quotes = false;
	size_t *quote_idx_l = NULL;
	size_t *quote_idx_r = NULL;
	size_t *quote_idx_l_new = NULL;
	size_t *quote_idx_r_new = NULL;
	size_t i, j, len, quote_idx, quote_idx_size = 4;
	char *new_S = NULL;

	// single characters
	Py_UCS4 s, t;

	// retrieve the string from the function arguments
	PyObject *S = NULL;
	if (!PyArg_ParseTuple(args, "O", &S)) {
		printf("Error parsing arguments.\n");
		return NULL;
	}

	// check that the string is ready
	if (PyUnicode_READY(S) == -1) {
		printf("Unicode object not ready.\n");
		return NULL;
	}

	// extract kind, data, and length
	kind = PyUnicode_KIND(S);
	data = PyUnicode_DATA(S);
	len = PyUnicode_GET_LENGTH(S);

	// empty string means return
	if (len == 0)
		return S;

	// initialize the arrays that'll hold the start and end indices of the
	// quoted parts of the string.
	quote_idx_l = malloc(sizeof(size_t) * quote_idx_size);
	if (quote_idx_l == NULL) {
		PyErr_NoMemory();
		return NULL;
	}
	quote_idx_r = malloc(sizeof(size_t) * quote_idx_size);
	if (quote_idx_r == NULL) {
		PyErr_NoMemory();
		return NULL;
	}

	// allocate and populate the output array
	new_S = malloc(sizeof(char) * len);
	if (new_S == NULL) {
		PyErr_NoMemory();
		return NULL;
	}
	for (i=0; i<len; i++) {
		new_S[i] = '\0';
	}

	i = 0;
	quote_idx = 0;
	while (i < len) {
		s = PyUnicode_READ(kind, data, i);
		new_S[i] = s;

		if (s != 'Q') {
			i++;
			continue;
		}

		// record that we're starting a quoted bit
		if (!in_quotes) {
			in_quotes = true;
			quote_idx_l[quote_idx] = i;
			i += 1;
			continue;
		}

		// read the next character if we can
		if (i + 1 < len) {
			t = PyUnicode_READ(kind, data, i + 1);
		}
		if (i + 1 < len && t == 'Q') {
			i++;
		} else {
			quote_idx_r[quote_idx] = i;
			quote_idx++;
			in_quotes = false;

			// reallocate if we need to
			if (quote_idx == quote_idx_size) {
				quote_idx_size *= 2;
				quote_idx_l_new = quote_idx_l;
				quote_idx_l_new = realloc(quote_idx_l_new, sizeof(size_t)*quote_idx_size);
				if (quote_idx_l_new == NULL) {
					PyErr_NoMemory();
					return NULL;
				}
				quote_idx_r_new = quote_idx_r;
				quote_idx_r_new = realloc(quote_idx_r_new, sizeof(size_t)*quote_idx_size);
				if (quote_idx_r_new == NULL) {
					PyErr_NoMemory();
					return NULL;
				}
				quote_idx_l = quote_idx_l_new;
				quote_idx_r = quote_idx_r_new;
			}
		}
		i++;
	}

	// overwrite the part of the output string that's in quotes
	for (j=0; j<quote_idx; j++) {
		for (i=quote_idx_l[j]; i<=quote_idx_r[j]; i++) {
			new_S[i] = 'C';
		}
	}

	// convert to Python object
	PyObject *new_S_obj = PyUnicode_FromStringAndSize(new_S, (Py_ssize_t)len);
	if (new_S_obj == NULL)
		goto merge_err;
	Py_INCREF(new_S_obj);

merge_err:
	free(new_S);
	free(quote_idx_l);
	free(quote_idx_r);
	return new_S_obj;
}

/*
 * MODULE
 */

PyDoc_STRVAR(cabstraction_module_doc,
		"Helpers for abstraction computation in C\n");
PyDoc_STRVAR(cabstraction_base_abstraction_doc, "");
PyDoc_STRVAR(cabstraction_c_merge_with_quotechar_doc, "");

static struct PyMethodDef cabstraction_methods[] = {
	{ "base_abstraction", (PyCFunction)base_abstraction, METH_VARARGS,
		cabstraction_base_abstraction_doc },
	{ "c_merge_with_quotechar", (PyCFunction)c_merge_with_quotechar, METH_VARARGS,
		cabstraction_c_merge_with_quotechar_doc },
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"clevercsv.cabstraction",
	cabstraction_module_doc,
	-1,
	cabstraction_methods,
	NULL,
	NULL,
	NULL,
	NULL
};

PyMODINIT_FUNC PyInit_cabstraction(void)
{
	PyObject *module;
	module = PyModule_Create(&moduledef);
	if (module == NULL)
		return NULL;

	if (PyModule_AddStringConstant(module, "__version__",
				MODULE_VERSION) == -1)
		return NULL;
	return module;
}
