var overall_property = {
    view:"property",
    id:"sets",
    elements:[
        { label:"CASH SWEEP", type:"text", id:"width",
            value: overall_data.cash_sweep, format:bpEffect },
        { label:"P/L YTD", type:"text", id:"width",
            value: overall_data.pl_ytd, format:bpEffect },
        { label:"BP ADJUST", type:"text", id:"width",
            value: overall_data.futures_bp, format:bpEffect },
        { label:"FUTURES BP", type:"text", id:"width",
            value: overall_data.bp_adjustment, format:bpEffect },
        { label:"AVAILABLE $", type:"text", id:"width",
            value: overall_data.available_dollars, format:bpEffect },
        { label:"End of Day", type:"text", id:"width",
            value: overall_data.date, format:webix.i18n.dateFormatStr }
    ],
    autoheight:true,
    autowidth:true,
    editable:false
};

var overall_ui = {
    multi: true,
    view: "accordion",
    cols: [
        { header:"Overall", body: overall_property, width: 250 }
    ],
    collapsed: false
};