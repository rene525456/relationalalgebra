/*
 *
 * RZ nueva implementación con jQuery-console
 * */
jQuery(document).ready(function($) {
    $('#terminal').terminal(function(command, term) {
        if (command == 'ayuda') {
            term.echo("Esta es la ayuda: osea no hay ayuda");
            return;
        } 

        term.push(function(command, term) {
            term.pause();
            $.jrpc("ask.json", "query", 
                   [command],
                   function(data) {
                       term.resume();
                       if (data.error && data.error.message) {
                           term.error(data.error.message);
                       } else {
                           if (typeof data.result == 'boolean') {
                               term.echo(data.result ? 'aceptado' : 'fail');

                           } else if(typeof data.result == 'string'){
                               term.echo(data.result);
                           
                           } else {
                               var len = data.result.length;
                               for(var i=0;i<len; ++i) {
                                   term.echo(data.result[i].join(' | '));
                               }
                           }
                       }
                   },
                   // error function
                   function(xhr, status, error) {
                       term.error('[AJAX] ' + status +
                                  ' - Server reponse is: \n' +
                                  xhr.responseText);
                       term.resume();
                   });
        },
        {
            name: 'relational',
            prompt: 'relational> ',
            greetings: "terminal relational",
            onBlur: function() {
                // prevent loosing focus
                return false;
            }
        }
        );
    }, 
    // opciones
        {
            name: 'relational',
            prompt: 'relational> ',
            greetings: "terminal relational",
            onBlur: function() {
                // prevent loosing focus
                return false;
            }
        }
                           
    );
});
