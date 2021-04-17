/**
 * @file parser.c
 * @author G.J.J. van den Burg
 * @date 2019-02-13
 * @brief CleverCSV Python Parser object
 *
 * Copyright (c) The Alan Turing Institute.
 * See the LICENSE file for licensing information.
 *
 * @details
 * This implementation is a minor (but important) modification of the CSV 
 * module in CPython. In particular, we change the LL(1) parser to an LL(2) 
 * parser to remove the need to specify double quotes. We also add the option 
 * to return whether a cell was quoted or not, which is used in type 
 * detection.
 */


// NOTE: The name of this module is "cparser"

#define MODULE_VERSION "1.0"

#include "Python.h"
#include "structmember.h"

typedef struct {
	PyObject *error_obj;
} _cparserstate;

#define _cparserstate(o) ((_cparserstate *)PyModule_GetState(o))

static int _cparser_clear(PyObject *m)
{
	Py_CLEAR(_cparserstate(m)->error_obj);
	return 0;
}

static int _cparser_traverse(PyObject *m, visitproc visit, void *arg)
{
	Py_VISIT(_cparserstate(m)->error_obj);
	return 0;
}

static void _cparser_free(void *m)
{
	_cparser_clear((PyObject *)m);
}

static struct PyModuleDef _cparsermodule;

#define _cparserstate_global ((_cparserstate *)PyModule_GetState(PyState_FindModule(&_cparsermodule)))

typedef enum {
	START_RECORD,
	START_FIELD,
    	ESCAPED_CHAR,
    	IN_FIELD,
    	IN_QUOTED_FIELD,
    	ESCAPE_IN_QUOTED_FIELD,
    	QUOTE_IN_QUOTED_FIELD,
    	EAT_CRNL,
    	AFTER_ESCAPED_CRNL,
} ParserState;

typedef struct {
	PyObject_HEAD

		PyObject *input_iter;

	PyObject *fields;
	Py_UCS4 *field;
	Py_ssize_t field_size;
	Py_ssize_t field_len;
	long field_limit;

	Py_UCS4 delimiter;
	Py_UCS4 quotechar;
	Py_UCS4 escapechar;
	int doublequote;
	int strict;
	int return_quoted;

	ParserState state;
} ParserObj;

static PyTypeObject Parser_Type;

#define ParserObject_Check(v)   (Py_TYPE(v) == &Parser_Type)

/*
 * HELPERS
 */
static int _set_bool(const char *name, int *target, PyObject *src, int dflt)
{
	if (src == NULL)
		*target = dflt;
	else {
		int b = PyObject_IsTrue(src);
		if (b < 0)
			return -1;
		*target = b;
	}
	return 0;
}

static int _set_long(const char *name, long *target, PyObject *src, int dflt)
{
	if (src == NULL)
		*target = dflt;
	else {
		long value;
		if (!PyLong_CheckExact(src)) {
			PyErr_Format(PyExc_TypeError,
					"\"%s\" must be an integer", name);
			return -1;
		}
		value = PyLong_AsLong(src);
		if (value == -1 && PyErr_Occurred()) {
			return -1;
		}
		*target = value;
	}
	return 0;
}

static int _set_char(const char *name, Py_UCS4 *target, PyObject *src, Py_UCS4 dflt)
{
	if (src == NULL)
		*target = dflt;
	else {
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
	}
	return 0;
}



/*
 * PARSER
 */
static PyObject *_strstrip(PyObject *str, int strip_front, int strip_back)
{
	Py_ssize_t how_many = PyUnicode_GetLength(str) - strip_front - strip_back;
	PyObject *new = PyUnicode_New(how_many, PyUnicode_MAX_CHAR_VALUE(str));
	PyUnicode_CopyCharacters(new, 0, str, strip_front, how_many);
	Py_DECREF(str);
	return new;
}

static int _strstartswith(PyObject *str, Py_UCS4 c)
{
	Py_ssize_t len = PyUnicode_GetLength(str);
	return (len > 0) && PyUnicode_ReadChar(str, 0) == c;
}

static int _strendswith(PyObject *str, Py_UCS4 c)
{
	Py_ssize_t len = PyUnicode_GetLength(str);
	return (len > 0) && PyUnicode_ReadChar(str, len - 1) == c;
}

static int _quotecond(PyObject *field, Py_ssize_t field_len, Py_UCS4 q)
{
	if (q == '\0')
		return 0;
	if (field_len <= 1)
		return 0;
	return (_strstartswith(field, q) && _strendswith(field, q));
}

static int parse_save_field(ParserObj *self, int trailing)
{
	int is_quoted = 0;

	PyObject *field = PyUnicode_FromKindAndData(PyUnicode_4BYTE_KIND,
			(void *) self->field, self->field_len);
	if (field == NULL) {
		return -1;
	}

	// strip quotes if quoted string
	if (_quotecond(field, self->field_len, self->quotechar)) {
		field = _strstrip(field, 1, 1);
		is_quoted = 1;
	}

	// strip partial quotes if trailing at end of file
	if (trailing && _strstartswith(field, self->quotechar)) {
		field = _strstrip(field, 1, 0);
		is_quoted = 1;
	}

	self->field_len = 0;
	if (self->return_quoted > 0) {
		PyObject *tuple = PyTuple_New(2);
		if (PyTuple_SetItem(tuple, 0, field) < 0) {
			Py_DECREF(tuple);
			Py_DECREF(field);
			return -1;
		}
		PyObject *tf = is_quoted ? Py_True : Py_False;
		Py_INCREF(tf);
		if (PyTuple_SetItem(tuple, 1, tf) < 0) {
			Py_DECREF(tuple);
			Py_DECREF(tf);
			return -1;
		}
		if (PyList_Append(self->fields, tuple) < 0) {
			Py_DECREF(tuple);
			return -1;
		}
		Py_DECREF(tuple);
	} else {
		if (PyList_Append(self->fields, field) < 0) {
			Py_DECREF(field);
			return -1;
		}
		Py_DECREF(field);
	}

	return 0;
}

static int parse_grow_buff(ParserObj *self)
{
	assert((size_t)self->field_size <= PY_SSIZE_T_MAX / sizeof(Py_UCS4));

	Py_ssize_t field_size_new = self->field_size ? 2 * self->field_size : 4096;
	Py_UCS4 *field_new = self->field;
	PyMem_Resize(field_new, Py_UCS4, field_size_new);
	if (field_new == NULL) {
		PyErr_NoMemory();
		return 0;
	}
	self->field = field_new;
	self->field_size = field_size_new;
	return 1;
}

static int parse_add_char(ParserObj *self, Py_UCS4 c)
{
	if (self->field_len >= self->field_limit) {
		PyErr_Format(_cparserstate_global->error_obj, "field larger than field limit (%ld)",
				self->field_limit);
		return -1;
	}
	if (self->field_len == self->field_size && !parse_grow_buff(self))
		return -1;
	self->field[self->field_len++] = c;
	return 0;
}

static int parse_process_char(ParserObj *self, Py_UCS4 u, Py_UCS4 v)
{
	switch (self->state) {
		case START_RECORD:
			if (u == '\0') {
				break;
			} else if (u == '\r' || u == '\n') {
				self->state = EAT_CRNL;
				break;
			}
			self->state = START_FIELD;
			/* fallthru */
		case START_FIELD:
			if (u == '\r' || u == '\n' || u == '\0') {
				if (parse_save_field(self, 0) < 0)
					return -1;
				self->state = (u == '\0' ? START_RECORD : EAT_CRNL);
			} else if (u == self->quotechar) {
				if (parse_add_char(self, u) < 0)
					return -1;
				self->state = IN_QUOTED_FIELD;
			} else if (u == self->escapechar) {
				self->state = ESCAPED_CHAR;
			} else if (u == self->delimiter) {
				if (parse_save_field(self, 0) < 0)
					return -1;
			} else {
				if (parse_add_char(self, u) < 0)
					return -1;
				self->state = IN_FIELD;
			}
			break;
		case ESCAPED_CHAR:
			if (u == '\r' || u == '\n') {
				if (parse_add_char(self, u) < 0)
					return -1;
				self->state = AFTER_ESCAPED_CRNL;
				break;
			}
			if ( u != '\0' && u != self->delimiter &&
					u != self->escapechar &&
					u != self->quotechar) {
				if (parse_add_char(self, self->escapechar) < 0)
					return -1;
			}
			if (u == '\0')
				;
			else
				if (parse_add_char(self, u) < 0)
					return -1;
			self->state = IN_FIELD;
			break;
		case AFTER_ESCAPED_CRNL:
			if (u == '\0')
				break;
			/* fallthru */
		case IN_FIELD:
			if (u == '\r' || u == '\n' || u == '\0') {
				// EOL return [fields]
				if (parse_save_field(self, 0) < 0)
					return -1;
				self->state = (u == '\0') ? START_RECORD :
					EAT_CRNL;
			} else if (u == self->escapechar) {
				self->state = ESCAPED_CHAR;
			} else if (u == self->quotechar) {
				if (parse_add_char(self, u) < 0)
					return -1;
				self->state = IN_QUOTED_FIELD;
			} else if (u == self->delimiter) {
				if (parse_save_field(self, 0) < 0)
					return -1;
				self->state = START_FIELD;
			} else {
				if (parse_add_char(self, u) < 0)
					return -1;
			}
			break;
		case IN_QUOTED_FIELD:
			if (u == '\0')
				;
			else if (u == self->escapechar)
				self->state = ESCAPE_IN_QUOTED_FIELD;
			else if (u == self->quotechar) {
				if (v == self->quotechar) {
					self->doublequote = 1;
					self->state = QUOTE_IN_QUOTED_FIELD;
				} else if (self->strict) {
					PyErr_Format(_cparserstate_global->error_obj,
							"'%c' expected after '%c'",
							self->delimiter,
							self->quotechar);
					return -1;
				} else {
					if (parse_add_char(self, u) < 0)
						return -1;
					self->state = IN_FIELD;
				}
			} else {
				if (parse_add_char(self, u) < 0)
					return -1;
			}
			break;
		case ESCAPE_IN_QUOTED_FIELD:
			// only escape "escapable" characters
			if (u != self->escapechar && u != self->delimiter &&
					u != self->quotechar && u != '\0') {
				if (parse_add_char(self, self->escapechar) < 0)
					return -1;
			}
			if (u == '\0')
				u = '\n'; // TODO does this work with field_len?
			if (parse_add_char(self, u) < 0)
				return -1;
			self->state = IN_QUOTED_FIELD;
			break;
		case QUOTE_IN_QUOTED_FIELD:
			if (u == self->quotechar) {
				if (parse_add_char(self, u) < 0)
					return -1;
				self->state = IN_QUOTED_FIELD;
			} else if (u == self->delimiter) {
				if (parse_save_field(self, 0) < 0)
					return -1;
				self->state = START_FIELD;
			} else if (u == '\r' || u == '\n' || u == '\0') {
				if (parse_save_field(self, 0) < 0)
					return -1;
				self->state = (u == '\0') ? START_RECORD :
					EAT_CRNL;
			} else if (!self->strict) {
				if (parse_add_char(self, u) < 0)
					return -1;
				self->state = IN_FIELD;
			} else {
				PyErr_Format(_cparserstate_global->error_obj,
						"'%c' expected after '%c'",
						self->delimiter,
						self->quotechar);
				return -1;
			}
			break;
		case EAT_CRNL:
			if (u == '\r' || u == '\n')
				;
			else if (u == '\0')
				self->state = START_RECORD;
			else {
				PyErr_Format(_cparserstate_global->error_obj,
						"new-line character seen in unquoted field - do you need to open the file in universal-newline mode?");
				return -1;
			}
			break;
	}
	return 0;
}

static int parse_reset(ParserObj *self)
{
	Py_XSETREF(self->fields, PyList_New(0));
	if (self->fields == NULL)
		return -1;
	self->field_len = 0;
	self->state = START_RECORD;
	return 0;
}

static PyObject *Parser_iternext(ParserObj *self)
{
	PyObject *fields = NULL;
	Py_UCS4 u, v;
	Py_ssize_t pos, linelen;
	unsigned int kind;
	void *data;
	PyObject *lineobj;

	if (parse_reset(self) < 0)
		return NULL;
	do {
		lineobj = PyIter_Next(self->input_iter);
		if (lineobj == NULL) {
			/* End of input OR exception */
			if (!PyErr_Occurred() && (self->field_len != 0 ||
						self->state == IN_QUOTED_FIELD)) {
				if (self->strict) {
					PyErr_SetString(_cparserstate_global->error_obj,
							"unexpected end of data");
				} else if (parse_save_field(self, 1) >= 0) {
					break;
				}
			}
			return NULL;
		}
		if (!PyUnicode_Check(lineobj)) {
			PyErr_Format(_cparserstate_global->error_obj,
					"iterator should return strings, "
					"not %.200s "
					"(did you open the file in text mode?)",
					lineobj->ob_type->tp_name
				    );
			Py_DECREF(lineobj);
			return NULL;
		}
		if (PyUnicode_READY(lineobj) == -1) {
			Py_DECREF(lineobj);
			return NULL;
		}
		kind = PyUnicode_KIND(lineobj);
		data = PyUnicode_DATA(lineobj);
		pos = 0;
		linelen = PyUnicode_GET_LENGTH(lineobj);
		v = '\0';
		while (linelen--) {
			if (v != '\0')
				u = v;
			else
				u = PyUnicode_READ(kind, data, pos);
			if (linelen > 0)
				v = PyUnicode_READ(kind, data, pos+1);
			else
				v = '\0';

			if (u == '\0') {
				Py_DECREF(lineobj);
				PyErr_Format(_cparserstate_global->error_obj,
						"line contains NULL byte");
				goto err;
			}
			if (parse_process_char(self, u, v) < 0) {
				Py_DECREF(lineobj);
				goto err;
			}
			pos++;
		}
		Py_DECREF(lineobj);
		if (parse_process_char(self, 0, 0) < 0)
			goto err;
	} while (self->state != START_RECORD);

	fields = self->fields;
	self->fields = NULL;
err:
	return fields;

}

static void Parser_dealloc(ParserObj *self)
{
	PyObject_GC_UnTrack(self);
	Py_XDECREF(self->input_iter);
	Py_XDECREF(self->fields);
	if (self->field != NULL)
		PyMem_Free(self->field);
	PyObject_GC_Del(self);
}

static int Parser_traverse(ParserObj *self, visitproc visit, void *arg)
{
	Py_VISIT(self->input_iter);
	Py_VISIT(self->fields);
	return 0;
}

static int Parser_clear(ParserObj *self)
{
	Py_CLEAR(self->input_iter);
	Py_CLEAR(self->fields);
	return 0;
}

PyDoc_STRVAR(Parser_Type_doc,
		"CSV parser\n"
		"\n"
		"The CleverCSV parser converts data in CSV format to tabular data\n"
	    );

static struct PyMethodDef Parser_methods[] = {
	{ NULL, NULL }
};

#define P_OFF(x) offsetof(ParserObj, x)

static struct PyMemberDef Parser_memberlist[] = {
	{ "doublequote", T_INT, P_OFF(doublequote), READONLY },
	{ NULL }
};

static PyTypeObject Parser_Type = {
	PyVarObject_HEAD_INIT(NULL, 0)
		"cparser.Parser",
	sizeof(ParserObj),
	0,
	/* methods */
	(destructor)Parser_dealloc,
	(printfunc)0,
	(getattrfunc)0,
	(setattrfunc)0,
	0,
	(reprfunc)0,
	0,
	0,
	0,
	(hashfunc)0,
	(ternaryfunc)0,
	(reprfunc)0,
	0,
	0,
	0,
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
	Parser_Type_doc,
	(traverseproc)Parser_traverse,
	(inquiry)Parser_clear,
	0,
	0,
	PyObject_SelfIter,
	(getiterfunc)Parser_iternext,
	Parser_methods,
	Parser_memberlist,
	0,
};

static PyObject *cparser_parser(PyObject *module, PyObject *args, PyObject *keyword_args)
{
	ParserObj *self = PyObject_GC_New(ParserObj, &Parser_Type);

	PyObject *ret = NULL,
		 *delimiter = NULL,
		 *quotechar = NULL,
		 *escapechar = NULL,
		 *field_limit = NULL,
		 *strict = NULL,
		 *return_quoted = NULL,
		 *iterator = NULL;

	if (!self)
		return NULL;

	// set defaults
	self->fields = NULL;
	self->input_iter = NULL;
	self->field = NULL;
	self->field_size = 0;
	self->doublequote = 0;
	self->return_quoted = 0;

	if (parse_reset(self) < 0) {
		Py_DECREF(self);
		return NULL;
	}

	static char *kwlist[] = {
		"csvfile",
	       	"delimiter",
	       	"quotechar",
	       	"escapechar",
	       	"field_limit",
	       	"strict",
		"return_quoted",
	       	NULL
	};

	if (!PyArg_ParseTupleAndKeywords(args, keyword_args, "O|$OOOOOO", kwlist,
				&iterator, &delimiter, &quotechar, &escapechar, 
				&field_limit, &strict, &return_quoted)) {
		Py_DECREF(self);
		return NULL;
	}

	Py_XINCREF(delimiter);
	Py_XINCREF(quotechar);
	Py_XINCREF(escapechar);
	Py_XINCREF(field_limit);
	Py_XINCREF(strict);
	Py_XINCREF(return_quoted);

#define ATTRSET(meth, name, target, src, dflt) \
	if (meth(name, target, src, dflt)) \
	goto err

	ATTRSET(_set_char, "delimiter", &self->delimiter, delimiter, ',');
	ATTRSET(_set_char, "quotechar", &self->quotechar, quotechar, 0);
	ATTRSET(_set_char, "escapechar", &self->escapechar, escapechar, 0);
	ATTRSET(_set_long, "field_limit", &self->field_limit, field_limit, 128 * 1024);
	ATTRSET(_set_bool, "strict", &self->strict, strict, 0);
	ATTRSET(_set_bool, "return_quoted", &self->return_quoted, return_quoted, 0);

	self->input_iter = PyObject_GetIter(iterator);
	if (self->input_iter == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"argument 1 must be an iterator");
		Py_DECREF(self);
		return NULL;
	}

	PyObject_GC_Track(self);
	ret = (PyObject *)self;
	Py_INCREF(self);

err:
	Py_XDECREF(self);
	Py_XDECREF(delimiter);
	Py_XDECREF(quotechar);
	Py_XDECREF(escapechar);
	Py_XDECREF(field_limit);
	Py_XDECREF(strict);
	Py_XDECREF(return_quoted);

	return ret;
}

/*
 * MODULE
 */

PyDoc_STRVAR(cparser_module_doc,
		"CleverCSV Parser in C\n");

PyDoc_STRVAR(cparser_parser_doc,
		"    cparser.Parser = Parser(iterable, delimiter='', quotechar='', \n"
		"                            escapechar='', field_limit=128*1024)\n");

static struct PyMethodDef cparser_methods[] = {
	{ "Parser", (PyCFunction)cparser_parser,
		METH_VARARGS | METH_KEYWORDS, cparser_parser_doc},
	{ NULL, NULL }
};

static struct PyModuleDef _cparsermodule = {
	PyModuleDef_HEAD_INIT,
	"ccsv.cparser",
	cparser_module_doc,
	sizeof(_cparserstate),
	cparser_methods,
	NULL,
	_cparser_traverse,
	_cparser_clear,
	_cparser_free
};

PyMODINIT_FUNC PyInit_cparser(void)
{
	PyObject *module;

	if (PyType_Ready(&Parser_Type) < 0)
		return NULL;

	/* Create the module and add the functions */
	module = PyModule_Create(&_cparsermodule);
	if (module == NULL)
		return NULL;

	/* Add version to the module. */
	if (PyModule_AddStringConstant(module, "__version__",
				MODULE_VERSION) == -1)
		return NULL;


	/* Add the CSV exception object to the module. */
	_cparserstate(module)->error_obj = PyErr_NewException("cparser.Error", NULL, NULL);
	if (_cparserstate(module)->error_obj == NULL)
		return NULL;
	Py_INCREF(_cparserstate(module)->error_obj);
	PyModule_AddObject(module, "Error", _cparserstate(module)->error_obj);
	return module;
}
