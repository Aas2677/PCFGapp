
/* disable free text input into number box -- we only want the user to be able to use the scroll buttons
 so that the event listener can operate every time the input changes*/
$("[type='number']").keypress(function (evt) {
    evt.preventDefault();
});



// add eventlistener to the nth parse button 
const n_best_input = document.getElementById("a")
n_best_input.addEventListener('change',restrict_parse_button);

//keep track of the maximum number of parses we have gerated 
const max_parses = document.getElementById("max_number_parses").innerHTML
const parse_button =  document.getElementById("show_parses") 


// console.log(n_best_input.value)


function restrict_parse_button(){
    if( parseInt(n_best_input.value) > parseInt(max_parses)){
       
        parse_button.style.visibility = "hidden"
    } 
    else{
        parse_button.style.visibility = "visible"

    }
    
}