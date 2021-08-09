
/* disable free text input into number box -- we only want the user to be able to use the scroll buttons
 so that the event listener can operate every time the input changes*/
$("[type='number']").keypress(function (evt) {
    evt.preventDefault();
});



// add eventlistener to the nth parse button 
const n_best_input = document.getElementById("nth_parse")
const n_best_input_2 = document.getElementById("nth_parse_2")

n_best_input.addEventListener('change',restrict_parse_button);
n_best_input_2.addEventListener('change',restrict_parse_button_2);

//keep track of the maximum number of parses we have gerated 
const max_parses = document.getElementById("max_number_parses").innerHTML





//hide the show parses button if user tries to request a parse number that doesn't exist, also remove the master buttons 
function restrict_parse_button(){

    document.querySelectorAll('.all_button').forEach(e => e.remove());

    let parse_button =  document.getElementById("show_parses") 



   
    if( parseInt(n_best_input.value) > parseInt(max_parses)){
       
        parse_button.style.visibility = "hidden"
    } 
    else{
        parse_button.style.visibility = "visible"

    }
    
}

function restrict_parse_button_2(){

    document.querySelectorAll('.all_button_2').forEach(e => e.remove());

    let parse_button_2 =  document.getElementById("show_parses_2") 



   
    if( parseInt(n_best_input_2.value) > parseInt(max_parses)){
       
        parse_button_2.style.visibility = "hidden"
    } 
    else{
        parse_button_2.style.visibility = "visible"

    }
    
}




