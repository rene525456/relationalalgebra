# -*- coding: utf-8 -*-
# coding = UTF-8
# Relational
# Copyright (C) 2010  Salvo "LtWorf" Tomaselli
#
# Relational is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>
# Initial readline code from http://www.doughellmann.com/PyMOTW/readline/index.html

import readline
import logging
import os.path
import os
import sys

from relational import relation, parser, rtypes
from termcolor import colored


class SimpleCompleter(object):
    '''Handles completion'''

    def __init__(self, options):
        '''Takes a list of valid completion options'''
        self.options = sorted(options)
        return

    def add_completion(self, option):
        '''Adds one string to the list of the valid completion options'''
        if option not in self.options:
            self.options.append(option)
            self.options.sort()

    def remove_completion(self, option):
        '''Removes one completion from the list of the valid completion options'''
        if option in self.options:
            self.options.remove(option)
        pass

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:

                self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]

                #Add the completion for files here
                try:
                    d = os.path.dirname(text)
                    listf = os.listdir(d)

                    d += "/"
                except:
                    d = ""
                    listf = os.listdir('.')

                for i in listf:
                    i = (d + i).replace('//', '/')
                    if i.startswith(text):
                        if os.path.isdir(i):
                            i = i + "/"
                        self.matches.append(i)

                logging.debug('%s matches: %s', repr(text), self.matches)
            else:
                self.matches = self.options[:]
                logging.debug('(empty input) matches: %s', self.matches)

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug('complete(%s, %s) => %s',
                      repr(text), state, repr(response))
        return response


relations = {}
completer = SimpleCompleter(['SURVEY', 'LIST', 'LOAD ', 'UNLOAD ', 'HELP ', 'QUIT', 'SAVE ', '_PRODUCT ', '_UNION ', '_INTERSECTION ', '_DIFFERENCE ', '_JOIN ', '_LJOIN ', '_RJOIN ', '_FJOIN ', '_PROJECTION ', '_RENAME_TO ', '_SELECTION ', '_RENAME ', '_DIVISION '])


def load_relation(filename, defname=None):
    if not os.path.isfile(filename):
        print >> sys.stderr, colored("%s is not a file" % filename, 'red')
        return None

    f = filename.split('/')
    if defname == None:
        defname = f[len(f)-1].lower()
        if defname.endswith(".csv"): #removes the extension
            defname = defname[:-4]

    if not rtypes.is_valid_relation_name(defname):
        print >> sys.stderr, colored("%s is not a valid relation name" % defname,'red')
        return
    try:
        relations[defname]=relation.relation(filename)

        completer.add_completion(defname)
        print colored("Loaded relation %s"% defname,'green', attrs=['bold'])
        return defname
    except Exception, e:
        print >>sys.stderr, colored(e,'red')
        return None

def survey():
    '''performs a survey'''
    from relational import maintenance

    post= {'software':'Relational algebra (cli)', 'version':'version'}

    fields=('System', 'Country', 'School', 'Age', 'How did you find', 'email (only if you want a reply)', 'Comments')
    for i in fields:
        a = raw_input('%s: '%i)
        post[i]=a
    maintenance.send_survey(post)

def help(command):
    '''Prints help on the various functions'''
    p = command.split(' ', 1)
    if len(p)==1:
        print 'HELP command'
        print 'To execute a query:\n[relation =] query\nIf the 1st part is omitted, the result will be stored in the relation last_.'
        print 'To prevent from printing the relation, append a ; to the end of the query.'
        print 'To insert relational operators, type _OPNAME, they will be internally replaced with the correct symbol.'
        print 'Rember: the tab key is enabled and can be very helpful if you can\'t remember something.'
        return
    cmd = p[1]

    if cmd=='QUIT':
        print 'Quits the program'
    elif cmd=='LIST':
        print "Lists the relations loaded"
    elif cmd=='LOAD':
        print "LOAD filename [relationame]"
        print "Loads a relation into memory"
    elif cmd=='UNLOAD':
        print "UNLOAD relationame"
        print "Unloads a relation from memory"
    elif cmd=='SAVE':
        print "SAVE filename relationame"
        print "Saves a relation in a file"
    elif cmd=='HELP':
        print "Prints the help on a command"
    elif cmd=='SURVEY':
        print "Fill and send a survey"
    else:
        print "Unknown command: %s" %cmd


def mi_exec_line(command):
    command = command.strip()

    if command.startswith(';'):
        return
    elif command.startswith('HELP'):
        help(command)
    elif command == 'LIST':         # Lists all the loaded relations
        out = ""
        for i in relations:
            if not i.startswith('_'):
                out += i
        return out
    elif command == 'SURVEY':
        survey()
    elif command.startswith('LOAD '):      # Loads a relation
        pars = command.split(' ')
        if len(pars) == 1:
            out = colored("Missing parameter", 'red')
            return out

        filename = pars[1]
        if len(pars) > 2:
            defname = pars[2]
        else:
            defname = None
        load_relation(filename, defname)

    elif command.startswith('UNLOAD '):
        pars = command.split(' ')
        if len(pars) < 2:
            out = colored("Missing parameter", 'red')
            return out
        if pars[1] in relations:
            del relations[pars[1]]
            completer.remove_completion(pars[1])
        else:
            out = colored("No such relation %s" % pars[1], 'red')
            return out
        pass
    elif command.startswith('SAVE '):
        pars = command.split(' ')
        if len(pars) != 3:
            out = colored("Missing parameter", 'red')
            return out

        filename = pars[1]
        defname = pars[2]

        if defname not in relations:
            out = colored("No such relation %s" % defname, 'red')
            return out

        try:
            relations[defname].save(filename)
        except Exception, e:
            out = colored(e, 'red')
            return out
    else:
        exec_query(command)


def exec_line(command):
    command = command.strip()

    if command.startswith(';'):
        return
    elif command=='QUIT':
        sys.exit(0)
    elif command.startswith('HELP'):
        help(command)
    elif command=='LIST':         #Lists all the loaded relations
        for i in relations:
            if not i.startswith('_'):
                print i
    elif command=='SURVEY':
        survey()
    elif command.startswith('LOAD '):      #Loads a relation
        pars = command.split(' ')
        if len(pars)==1:
            print colored("Missing parameter",'red')
            return

        filename = pars[1]
        if len(pars)>2:
            defname = pars[2]
        else:
            defname = None
        load_relation(filename, defname)

    elif command.startswith('UNLOAD '):
        pars = command.split(' ')
        if len(pars)<2:
            print colored("Missing parameter",'red')
            return
        if pars[1] in relations:
            del relations[pars[1]]
            completer.remove_completion(pars[1])
        else:
            print colored("No such relation %s" % pars[1],'red')
        pass
    elif command.startswith('SAVE '):
        pars = command.split(' ')
        if len(pars)!=3:
            print colored("Missing parameter",'red')
            return

        filename = pars[1]
        defname = pars[2]

        if defname not in relations:
            print colored("No such relation %s" % defname,'red')
            return

        try:
            relations[defname].save(filename)
        except Exception, e:
            print colored(e,'red')
    else:
        exec_query(command)

def replacements(query):
    '''This funcion replaces ascii easy operators with the correct ones'''
    query = query.replace(    '_PRODUCT'          ,   '*')
    query = query.replace(    '_UNION'            ,   'ᑌ')
    query = query.replace(    '_INTERSECTION'     ,   'ᑎ')
    query = query.replace(    '_DIFFERENCE'       ,   '-')
    query = query.replace(    '_JOIN'             ,   'ᐅᐊ')
    query = query.replace(    '_LJOIN'            ,   'ᐅLEFTᐊ')
    query = query.replace(    '_RJOIN'            ,   'ᐅRIGHTᐊ')
    query = query.replace(    '_FJOIN'            ,   'ᐅFULLᐊ')
    query = query.replace(    '_PROJECTION'       ,   'π')
    query = query.replace(    '_RENAME_TO'        ,   '➡')
    query = query.replace(    '_SELECTION'        ,   'σ')
    query = query.replace(    '_RENAME'           ,   'ρ')
    query = query.replace(    '_DIVISION'         ,   '÷')
    return query


def exec_query(command):
    '''This function executes a query and prints the result on the screen
    if the command terminates with ";" the result will not be printed
    '''

    #If it terminates with ; doesn't print the result
    if command.endswith(';'):
        command = command[:-1]
        printrel = False
    else:
        printrel = True

    # RZ avisamos que estamos enviando un utf-8 para que no se complique
    command = command.encode('utf-8')
    #Performs replacements for weird operators
    command = replacements(command)

    #Finds the name in where to save the query
    parts = command.split('=', 1)

    if len(parts) > 1 and rtypes.is_valid_relation_name(parts[0]):
        relname = parts[0]
        query = parts[1]
    else:
        relname = 'last_'
        query = command

    query = unicode(query, 'utf-8')
    #Execute query
    try:
        pyquery = parser.parse(query)
        result = eval(pyquery, relations)
        out = colored("-> query: %s" % pyquery, 'green')

        if printrel:
            out += ""
            out += str(result)

        relations[relname] = result

        completer.add_completion(relname)
        print "DEBUG " + out
        return out
    except Exception, e:
        print colored(e, 'red')


def main(files=[]):
    print colored('> ', 'blue') + "; Type HELP to get the HELP"
    print colored('> ', 'blue') + "; Completion is activated using the tab (if supported by the terminal)"

    for i in files:
        load_relation(i)

    readline.set_completer(completer.complete)

    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode emacs')
    readline.set_completer_delims(" ")


    while True:
        try:
            line = raw_input(colored('> ', 'blue'))
            if isinstance(line, str) and len(line)>0:
                exec_line(line)
        except EOFError:
            print
            sys.exit(0)


if __name__ == "__main__":
    main()

