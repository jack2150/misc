function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function intOnly(theNumber)
{
    if (theNumber == '-' || theNumber == 0) {
        return '-';
    }
    else {
        return Number(theNumber);
    }
}

function numOnly(theNumber)
{
    if (theNumber == '-' || theNumber == 0) {
        return '-';
    }
    else {
        if(theNumber > 0){
            return Number(theNumber).toFixed(2);
        }
        else{
            return Number(theNumber).toFixed(2);
        }
    }
}

function numWithPositive(theNumber)
{
    if (theNumber == '-' || theNumber == 0) {
        return '-';
    }
    else {
        if(theNumber > 0){
            return "+" + Number(theNumber).toFixed(2);
        }
        else{
            return Number(theNumber).toFixed(2);
        }
    }
}

function bpEffect(theNumber)
{
    if (theNumber == '-' || theNumber == 0) {
        return '-';
    }
    else {
        if(theNumber > 0){
            return numberWithCommas(Number(theNumber).toFixed(2));
        }
        else{
            theNumber *= -1;
            return "(" + numberWithCommas(Number(theNumber).toFixed(2)) + ")";
        }
    }
}


function pctChange(theNumber)
{
    if (theNumber == '-' || theNumber == 0) {
        return '-';
    }
    else {
        if(theNumber > 0){
            return "+" + Number(theNumber).toFixed(2) + "%";
        }
        else{
            return Number(theNumber).toFixed(2) + "%";
        }
    }
}