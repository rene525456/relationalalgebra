/*
 *
 * RZ nueva implementación con jQuery-console
 * This is the best and most succesful
 * */
jQuery(document).ready(function($) {

    // formatear el texto
    function formatear(t){
        // split by \n
        var partes = t.split("\n");
        var out = "<b>" + partes[0] + "</b><br>";
        if (partes.length>1){
            for(var i=1;i<partes.length;i++){
                out += partes[i] + "<br>";
            }
        }
        return out;
    }

    // que pasa cuando cambiamos algo en la linea de comandos?
    function conversar(e){
        //var s = $(this).val().split(" ");
        var s = $(this).val();
        var promise = comunicar(s);
        if (s.indexOf('=') !== -1){
            //promise.then(function(){
                get_relaciones();
            //});
        }
        return promise;
    }

    function comunicar(s){
        var l = s.split(" ");
        var request = JSON.stringify({
           'jsonrpc': '2.0', 'method': "post",
            'params': l});

        return $.ajax({
            type: "POST",
            url: "ask.json",
            contentType: 'application/json',
            dataType: 'text',
            async: true,
            cache: false,
            data: request,
            success: function(data){
                var data1 = JSON.parse(data);
                if (data1.error){
                    console.log("error: " + data1.error);
                    alert("ERROR: " + data1.error);
                } else if(typeof data1.result == 'string'){
                    //$('#pantalla').html(formatear(data1.result));
                    $('#pantalla pre').html(data1.result);
                } else {
                    var len = data1.result.length;
                    for(var i=0;i<len; ++i) {
                        $("#pantalla pre").html(echo(data1.result[i].join(' | ')));
                    }
                }

                if(!data1.error && data1.esto === 'funciona'){
                    // agregar el comando a la lista
                    if($('div#lasts a').length > 9){
                        $('div#lasts a').remove(0);
                    }
                    $('div#lasts').append('<a href="#" class="list-group-item">'+ s +'</a>');
                    $('#lasts').scrollTop($('#lasts').height());
                }
            }

        });
    }

    function get_relaciones(){
        return $.ajax({
            type: "GET",
            url: "relaciones.json",
            contentType: 'application/json',
            dataType: 'text',
            async: true,
            cache: false,
            success: function(data){
                var data1 = JSON.parse(data);
                if (data1.error){
                    console.log("error: " + data1.error);
                    alert("ERROR: " + data1.error);
                }else{
                    $('#panel-relaciones').empty()
                    $.each(data1.result, function(i, v){
                        $("#panel-relaciones").append("<li class='list-group-item'>"+v+"</li>");
                    });
                }
            }

        });

    }

    $('input[name=comando]').bind("enterKey", conversar);

    $('input[name=comando]').keyup(function(e){
        if(e.keyCode == 13){
            $(this).trigger("enterKey");
            $("input[name=comando]").val("");
        }
    });

    // manejo de botones de operadores
    $(".operadores").on("click", function(e){
        if ($(this).hasClass("nodelete")){
            var prev = $("input[name=comando]").val();
            $("input[name=comando]").val(prev + " " + $(this).data("name"));
        }else{
            $("input[name=comando]").val("");
            $("input[name=comando]").val($(this).data("name"));
        }

        $("input[name=comando]").focus();
    });

    $("button[name=ejecutar]").on("click", conversar);

    $("button[name=borrar]").on("click", function(e){
        $("input[name=comando]").val("");
    });

    // manejo del upload
    $('#upload-file-btn').click(function() {
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/upload.json',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function(data) {
                console.log('Success!');
                $("#modalCargar").modal("toggle");
                $("input[name=comando]").val("");
                var promise = comunicar("LOAD " + data[0].url);
                // Ok is loaded, now add to the list
                promise.success(function(resp){
                    var r = JSON.parse(resp);
                    if(r.esto && r.esto == 'funciona'){
                        //$("#panel-relaciones").append("<li class='list-group-item'>"+r.expr[1]+"</li>");
                        get_relaciones();
                    }
                });
            },
        });
    });

    // obtener los atributos de una relación
    $("#panel-relaciones").on("click", "li", function(e){
        $("#atributos").html("");

        $('#panel-relaciones li').removeClass('list-group-item-success');

        $(this).addClass('list-group-item-success');

        $.get("/atributos.json", {tabla: $(this).html()}, function(resp){
            resp.forEach(function(i){
                $("#atributos").append("<span class='badge badge-warning'>" + i + "</span>");
            });
        });
    });

    // handson table
    var data = [[]];

    var sr = $('#sheetrelation').handsontable({
        data: data,
        minSpareRows: 1,
        colHeaders: true,
        contextMenu: true,
        autoColumnSize: true,
        minCols: 11,
        minRows: 8
    });

    // for edit relations
    var sre = $('#sheetrelationedit').handsontable({
        data: data,
        minSpareRows: 1,
        colHeaders: true,
        contextMenu: true,
        autoColumnSize: true,
        minCols: 11,
        minRows: 8
    });

    // simple filename validator
    $('input[name=relname]').on('change', function(e){
        var fileReg = /^[a-z0-9]+$/i;
        $('input[name=relname]').parent().find('span').remove();
        $(this).parent().removeClass('has-error');

        if ($(this).val().match(fileReg)){
            $('button[name=guardar_relacion]').removeClass('disabled')
        }else{
            $('button[name=guardar_relacion]').addClass('disabled')
            $(this).parent().addClass('has-error');
            $(this).parent().append('<span class="help-block">nombre incorrecto</span>');
        }
        console.log('cambiando a ', $(this).val());
    });

    $('button[name=guardar_relacion]').on('click', function(e){
        // guardar la relación
        var ht = $('#sheetrelation').data('handsontable');
        var filename = $('#newRelationModal input[name=relname]').val();

        if($('#panel-relaciones li').filter(
            function(i, l){
            return l.innerHTML === filename}).length > 0 &&
            ht.getData().filter(function(e){ e.filter(function(i){ return i});}).length === 0){
                alert('Error no se puede crear una relación existente');
                return;
            }

            $('#panel-relaciones li').each(function(i, l){ if($(l).text());});

        $.ajax({
            type: "POST",
            url: "saverel.json",
            contentType: 'application/json',
            dataType: 'text',
            async: true,
            cache: false,
            data: JSON.stringify({filename: filename, data: ht.getData()}),

            success: function(data) {
                $('#newRelationModal').modal('hide');
                $('input[name=relname]').val('');
                ht.clear();

                var promise = comunicar("LOAD data/" + filename + ".csv");
                // Ok is loaded, now add to the list
                promise.success(function(resp){
                    var r = JSON.parse(resp);
                    if(r.esto && r.esto == 'funciona'){
                        get_relaciones();
                        //$("#panel-relaciones").append("<li class='list-group-item'>"+r.expr[1]+"</li>");
                    }
                });
            },
        });
    });

    // modal editar
    $('button[name=modal_editar]').on('click', function(e){
        // only work if relation has been selected
        var relname = $('#panel-relaciones li.list-group-item-success');
        if(relname.length > 0){
            $('#editRelationModal').modal('show');
        }
    });

    // guardar la relación que está editada del modal
    $('button[name=editar_relacion]').on('click', function(e){
        var ht = $('#sheetrelationedit').data('handsontable');
        var filename = $('#editRelationModal input[name=relname]').val();
        $.ajax({
            type: "POST",
            url: "saverel.json",
            contentType: 'application/json',
            dataType: 'text',
            async: true,
            cache: false,
            data: JSON.stringify({filename: filename, data: ht.getData()}),

            success: function(data) {
                $('#editRelationModal').modal('hide');
                $('#editRelationModal input[name=relname]').val('');
                ht.clear();

                var promise = comunicar("LOAD data/" + filename + ".csv");
                // Ok is loaded, now add to the list
                promise.success(function(resp){
                    var r = JSON.parse(resp);
                    if(r.esto && r.esto == 'funciona'){
                        get_relaciones();
                        //$("#panel-relaciones").append("<li class='list-group-item'>"+r.expr[1]+"</li>");
                    }
                });
            },
        });
    });

    $('#editRelationModal').on('show.bs.modal', function(e){
        // load the selected relation
        var relname = $('#panel-relaciones li.list-group-item-success').html();
        var request = JSON.stringify({
           'jsonrpc': '2.0', 'method': "post",
           'rand': new Date().getTime(),
           'params': relname});

        $.ajax({
            type: "POST",
            url: "editrel.json",
            contentType: 'application/json',
            dataType: 'text',
            async: true,
            cache: false,
            data: request,
            success: function(data){
                var data1 = JSON.parse(data);
                if (data1.error){
                    console.log("error: " + data1.error);
                    alert("ERROR: " + data1.error);
                } else {
                    console.log('debug',  data1.result);
                    $('#editRelationModal input[name=relname]').val(relname);
                    sre.data('handsontable').loadData(data1.result);
                }
            }

        });
    });

    // redo the last command on click
    $('div#lasts').on('click', 'a', function(e){
        var v = $(e.target).text();
        $("input[name=comando]").val(v);
        $("input[name=comando]").focus();
    });

    // quitar relacion
    $('button[name=quitar_relacion]').on('click', function(e){
        // funcionar solo si se ha seleccionado una relación
        var relname = $('#panel-relaciones li.list-group-item-success');
        if(relname.length > 0){
            if (confirm('Desea eliminar la relación '+relname.html()+'?')){
                var promise = comunicar('UNLOAD ' + relname.html());
                promise.success(function(resp){
                    var r = JSON.parse(resp);
                    if(r.esto && r.esto == 'funciona'){
                        get_relaciones();
                    }
                });
            }
        }
    });

    // esto se deberia ejecutar on load
    get_relaciones();
    // encerar el input
    $("input[name=comando]").val("");

    // borrar el historial
    $('button[name=limpiar]').on('click',function(){
        $('div#lasts a').each(function(i){ this.remove();});
    });

    // descargar una relación marcada
    $('button[name=descargar]').on('click',function(){
        var relname = $('#panel-relaciones li.list-group-item-success').html();
        if(relname){
            window.location.href = "/descargar/" + relname;
        }
    });
});
