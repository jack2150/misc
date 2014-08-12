var position_menu = {
    multi: true,
    collapsed: false,
    view: "accordion",
    cols: [
        {
            header:"Position Menu",
            body: {
                id: "position_menu",
                view:"list",
                data: [
                    { id:"position_view", value:"View Positions" },
                    { id:"position_import_select", value:"Import Positions" }
                ],
                select: true,
                scroll: false,
                width: 250,
                on:{
                    "onItemClick": function(id)
                    {
                        if (id == 'position_import_select') {
                            webix.send("{% url 'position_select_files' %}", null, 'GET')
                        }
                        if (id == 'position_view') {
                            webix.send("{% url 'position_view' %}", null, 'GET')
                        }

                    }
                }
            }
        }
    ]
};