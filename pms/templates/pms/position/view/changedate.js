var change_date = {
    multi: true,
    collapsed: false,
    view: "accordion",
    cols: [
        {
            header:"Change Date",
            body: {
                view:"calendar",
                id:"position_date",
                weekHeader:true,
                events:webix.Date.isHoliday,
                calendarDateFormat: "%Y-%m-%d",
                width:250,
                blockDates: function(date){
                    result = false;
                    // disable date before 2014
                    if(date.getFullYear()<2014)
                        result = true;
                    // disable sunday and saturday
                    else if (date.getDay() == 0 || date.getDay() == 6)
                        result = true;

                    return result;
                },
                on:{
                    "onDateSelect": function()
                    {
                        // get date and format into proper parameter
                        date = webix.Date.dateToStr("%Y-%m-%d")
                            ($$('position_date').getSelectedDate());

                        link = "{% url 'position_exists' %}" + date;

                        // ajax get date inside db
                        webix.ajax(link, function(text){
                            if (text == 'True') {
                                // redirect into select date
                                webix.send("{% url 'position_view' %}" + date, null, 'GET');
                            }
                            else {
                                 webix.message({ type:"error",
                                     text:date + " positions not found!" });
                            }
                        });
                    }
                }
            }
        }
    ]
};