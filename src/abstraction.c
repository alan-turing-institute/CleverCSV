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
			if (stack[len-1] != 'C')
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

/*
 * MODULE
 */

PyDoc_STRVAR(cabstraction_module_doc,
		"Helpers for abstraction computation in C\n");
PyDoc_STRVAR(cabstraction_base_abstraction_doc, "");

static struct PyMethodDef cabstraction_methods[] = {
	{ "base_abstraction", (PyCFunction)base_abstraction, METH_VARARGS,
		cabstraction_base_abstraction_doc },
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"ccsv.cabstraction",
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
