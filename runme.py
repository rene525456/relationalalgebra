#!/usr/bin/env python
# -*- coding: utf8 -*-

from flask import Flask, Response
#from flask import render_template, request, redirect, flash, url_for
from flask import render_template, request
from relational.relational_readline.webgui import mi_exec_line
from flask import json

app = Flask(__name__)


@app.route("/")
def inicio():
    """dispose the tryrelational.html code"""
    return render_template('relational.html')


@app.route("/consola")
def consola():
    """Este es el nuevo inicio para probar la nueva consola"""
    return render_template('consola.html')


@app.route("/gui")
def gui():
    """mejorando la pantalla del programa con relational"""
    return render_template('relational.html')


@app.route("/terminal")
def terminal():
    """Este es el nuevo inicio para probar la nueva consola"""
    return render_template('terminal.html')


@app.route("/ask.json", methods=['GET', 'POST'])
def ask():
    """esta funcion se complementa con el terminal para contestarle"""
    rj = json.loads(request.data)
    data = {}
    out = ""

    try:
        tmp = mi_exec_line(" ".join(rj['params']))
        out += tmp and str(tmp) or ""
        data["esto"] = "funciona"
    except Exception, e:
        data['error'] = e.__str__()
        data["esto"] = "error"

    data["expr"] = rj['params']
    data["result"] = out

    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')

    return resp


@app.route("/editrel.json", methods=['GET', 'POST'])
def editrel():
    """editar una relacion"""
    import csv

    rj = json.loads(request.data)
    tmp = []
    data = {}

    with open('data/%s.csv' % rj['params']) as f:
        cr = csv.reader(f)

        for row in cr:
            tmp.append(row)

    data["esto"] = "funciona"
    data["result"] = tmp

    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')

    return resp


@app.route("/relaciones.json", methods=['GET'])
def relaciones():
    """ver la lista de relaciones"""
    data = {}

    try:
        tmp = mi_exec_line("LIST ")
        'last_' in tmp and tmp.remove('last_')
    except Exception, e:
        data['error'] = e.__str__()

    data["esto"] = "funciona"
    data["expr"] = "LIST"
    data["result"] = tmp

    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')

    return resp


@app.route("/relational.json")
def relational():
    """la puerta al relational """
    expr = request.args.get('expr')

    data = """handleJSON({"type": "Relational", "expr": "%s", "result": "%s"})""" % \
             (expr, mi_exec_line(expr))

    resp = Response(data, status=200, mimetype='text/plain')

    return resp


@app.route("/upload.json", methods=['GET', 'POST'])
def upload():
    """subir los datas"""
    files = request.files.getlist('file')

    result = []
    for f in files:
        filename = f.filename
        file_size = f.content_length
        file_url = 'data/%s' % filename
        f.save(file_url)

        result.append({"name": filename,
                    "size": file_size,
                    "url": file_url,
                    "delete_url": file_url,
                    "delete_type": "POST"})

    js = json.dumps(result)

    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route("/saverel.json", methods=['POST'])
def saverel():
    """grabar la relacion a csv"""
    import csv

    data_content = json.loads(request.data)

    with open('data/%s.csv' % data_content['filename'], 'w') as f:
        cw = csv.writer(f)

        fdata = filter(lambda l: reduce(lambda x, y: x or y, l), data_content['data'])

        for row in fdata:
            cw.writerow([x for x in row if x is not None])

    result = {'status': 'ok'}
    js = json.dumps(result)

    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route("/atributos.json", methods=['GET'])
def atributos():
    """presentar los atributos de una tabla"""
    import csv
    tabla = request.args.get("tabla")

    # usar el módulo csv para ver los headers de esta cosa
    try:
        with open("data/%s.csv" % tabla) as f:
            reader = csv.reader(f)
            l = reader.next()
    except:
        l = ['no data']

    js = json.dumps(l)

    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route('/descargar/<tabla>', methods=['GET'])
def descargar(tabla):
    """descargar una relacion"""
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    with open("data/%s.csv" % tabla) as f:
        out = f.read()

    response = Response(out, mimetype='text/plain')
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = 'attachment; filename=%s.csv' % tabla

    return response

if __name__ == "__main__":
    app.run(debug=True)
