var import_button = {
    view:"button",
    value:"Import",
    width: 100,
    on:{
        "onItemClick": function(id, e, trg) {
            var file_date = $$('files_tree').getSelectedId();
            if (file_date != '-1' && file_date) {
                link = "{% url 'position_import_single' %}" + file_date + '/';
                //webix.send(link, null, "GET");
                webix.ajax(link, function(text){
                    webix.alert(
                        {
                            title:"Import Completed",
                            text: text,
                            width: "500px",
                            callback: function(){
                                webix.send("{% url 'position_select_files' %}", null, "GET");
                            }
                        }
                    );
                });
            }
            else {
                webix.message({ type:"error", text:"Please select file to import!" });
            }
        }
    }
};