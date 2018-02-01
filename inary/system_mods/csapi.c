/*
** Copyright (c) 2005, TUBITAK/UEKAE
**
** This program is free software; you can redistribute it and/or modify it
** under the terms of the GNU General Public License as published by the
** Free Software Foundation; either version 2 of the License, or (at your
** option) any later version. Please read the COPYING file.
*/

#include <Python.h>
#include <sys/time.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <net/route.h>
#include <unistd.h>
#include <string.h>

static PyObject *
csapi_atoi(PyObject *self, PyObject *args)
{
	char *str;
	int i;

	if (!PyArg_ParseTuple(args, "s", &str))
		return NULL;

	i = atoi(str);
	return Py_BuildValue("i", i);
}

static PyObject *
csapi_settimeofday(PyObject *self, PyObject *args)
{
	struct timeval tv;
	double t;

	if (!PyArg_ParseTuple(args, "d", &t))
		return NULL;

	tv.tv_sec = t;
	tv.tv_usec = 0;
	if (0 != settimeofday(&tv, NULL))
		return NULL;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
csapi_changeroute(PyObject *self, PyObject *args)
{
	struct rtentry route;
	struct sockaddr_in gw, dst, mask;

	int skfd, func;
	char *gw_ip, *dst_ip, *mask_ip;

	if (!PyArg_ParseTuple(args, "isss", &func, &gw_ip, &dst_ip, &mask_ip))
		return NULL;

	skfd = socket(AF_INET, SOCK_DGRAM, 0);

	if (skfd < 0)
		return NULL;

	memset(&gw, 0, sizeof(struct sockaddr));
	memset(&dst, 0, sizeof(struct sockaddr));
	memset(&mask, 0, sizeof(struct sockaddr));

	gw.sin_family = AF_INET;
	dst.sin_family = AF_INET;
	mask.sin_family = AF_INET;

	gw.sin_addr.s_addr = inet_addr(gw_ip);
	dst.sin_addr.s_addr = inet_addr(dst_ip);
	mask.sin_addr.s_addr = inet_addr(mask_ip);

	memset(&route, 0, sizeof(struct rtentry));
	route.rt_dst = *(struct sockaddr *)&dst;
	route.rt_gateway = *(struct sockaddr *)&gw;
	route.rt_genmask = *(struct sockaddr *)&mask;
	route.rt_flags = RTF_UP | RTF_GATEWAY;

	if(ioctl(skfd, func, &route) < 0) {
	    return NULL;
	}

	close(skfd);

	Py_INCREF(Py_None);
	return Py_None;
}


static PyMethodDef methods[] = {
	{ "atoi", csapi_atoi, METH_VARARGS,
		"Convert a string into an integer." },
	{ "settimeofday", csapi_settimeofday, METH_VARARGS,
		"Set system date." },
	{ "changeroute", csapi_changeroute, METH_VARARGS,
		"Change the route table."},
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef csapimodule ={
	PyModuleDef_HEAD_INIT,
	"csapi",
	NULL,
	-1,
	methods
};		

PyMODINIT_FUNC
PyInit_csapi(void)
{
	return PyModule_Create(&csapimodule);
}
