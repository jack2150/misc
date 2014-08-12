var position_ui = {
    view: "treetable",
    type: "space",
    columns: [
        { id:"name", header:"Name", width: 320, sort:"string",
            template:"{common.treetable()} #value#" },
        { id:"quantity", header:"Qty", sort:"int", format:intOnly },
        { id:"days", header:"Days", sort:"int", format:intOnly },
        { id:"trade_price", header:"Trade Price", sort:"int", format:numOnly },
        { id:"mark", header:"Mark", sort:"int", format:numOnly },
        { id:"mark_change", header:"M Change", sort:"int", format:numWithPositive },
        { id:"delta", header:"Delta", sort:"int", format:numWithPositive, footer:{ content:"summColumn" } },
        { id:"gamma", header:"Gamma", sort:"int", format:numWithPositive, footer:{ content:"summColumn" } },
        { id:"theta", header:"Theta", sort:"int", format:numWithPositive, footer:{ content:"summColumn" } },
        { id:"vega", header:"Vega", sort:"int", format:numWithPositive, footer:{ content:"summColumn" } },
        { id:"pct_change", header:"% Change", sort:"int", format:pctChange },
        { id:"pl_open", header:"P/L Open", sort:"int", format:numWithPositive, footer:{ content:"summColumn" } },
        { id:"pl_day", header:"P/L Day", sort:'int', format:numWithPositive, footer:{ content:"summColumn" } },
        { id:"bp_effect", header:"BP Effect", sort:'int', format:bpEffect, footer:{ content:"summColumn" }
 }
    ],
    autowidth: true,
    autoheight:true,
    footer:true,
    scrollY: true,
    scrollX: true,

    data: position_data
};