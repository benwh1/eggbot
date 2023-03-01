import { tiers, categories, data } from "./data.js";

const num_tiers = tiers.length;
const num_categories = categories.length;

function decompress(str){
    const pako = window.pako;
    var arr = pako.inflate(atob(str));
    var decoder = new TextDecoder();
    return decoder.decode(arr);
}

function format(time){
    if(time == -1){
        return "";
    }

    var t = time;
    var hours   = Math.floor(t/3600000); t %= 3600000;
    var minutes = Math.floor(t/60000);   t %= 60000;
    var seconds = Math.floor(t/1000);    t %= 1000;
    var millis  = t;

    if(time < 1000){
        return "0." + millis.toString().padStart(3, "0");
    }
    else if(time < 60000){
        return seconds + "." +
               millis.toString().padStart(3, "0");
    }
    else if(time < 3600000){
        return minutes + ":" +
               seconds.toString().padStart(2, "0") + "." +
               millis.toString().padStart(3, "0");
    }
    else{
        return hours + ":" +
               minutes.toString().padStart(2, "0") + ":" +
               seconds.toString().padStart(2, "0") + "." +
               millis.toString().padStart(3, "0");
    }
}

function result_tier(category, time){
    if(time == -1){
        return -1;
    }

    var tier;
    for(tier=0; tier<num_tiers; tier++){
        if(time == ""){
            break;
        }
        if(time > tiers[tier]["times"][category]){
            break;
        }
    }
    return tier-1;
}

function populate_table(table){
    var results_table = document.getElementById("results-table");

    // remove the previous table, if there was one
    while(results_table.hasChildNodes()){
        results_table.removeChild(results_table.firstChild);
    }

    // which user do we need to add to the table next?
    var next_user = 0;

    for(var i=num_tiers-1; i>=0; i--){
        const tier = tiers[i];
        const tier_name = tier["name"].toLowerCase();

        // table of all results of users in this tier
        var tier_table_wrapper = document.createElement("div");
        tier_table_wrapper.classList.add("table-wrapper")
        var tier_table = document.createElement("table");
        tier_table.id = tier_name + "-table";
        results_table.appendChild(tier_table_wrapper);

        // set up the header rows
        var tier_head = document.createElement("thead"); // header containing the following three rows
        var tier_name_row = document.createElement("tr"); // row containing the name of the tier
        var tier_req_row = document.createElement("tr"); // row containing the results required for the tier
        var tier_events_row = document.createElement("tr"); // row containing names of the categories

        tier_head.className = "table-header";
        tier_name_row.className = "tier-row";
        tier_req_row.className = "req-row";
        tier_events_row.className = "events-row";

        tier_table_wrapper.appendChild(tier_table);
        tier_table.appendChild(tier_head);
        tier_head.appendChild(tier_name_row);
        tier_head.appendChild(tier_req_row);
        tier_head.appendChild(tier_events_row);

        // tier name row
        var tier_name_div = document.createElement("td");

        // fill up the whole width of the table (columns = username, place, power, categories)
        tier_name_div.colSpan = num_categories+3;
        tier_name_div.textContent = tier["name"];

        tier_name_row.appendChild(tier_name_div);

        // tier requirements row
        for(var j=0; j<3; j++){
            tier_req_row.appendChild(document.createElement("td"));
        }
        tier_req_row.children[1].textContent = tier["power"];
        tier_req_row.children[2].textContent = tier["limit"];

        for(var j=0; j<num_categories; j++){
            var div = document.createElement("td");
            div.textContent = format(tier["times"][j]);
            tier_req_row.appendChild(div);
        }

        // tier events row
        for(var j=0; j<3; j++){
            tier_events_row.appendChild(document.createElement("td"));
        }
        tier_events_row.children[0].textContent = "Name";
        tier_events_row.children[1].textContent = "Place";
        tier_events_row.children[2].textContent = "Power";

        for(var j=0; j<num_categories; j++){
            var div = document.createElement("td");
            div.textContent = categories[j];
            tier_events_row.appendChild(div);
        }

        // add the users to the table
        while(true){
            const user = table[next_user];

            // if the user's power is too low, stop adding new rows
            if(user[2] < tier["limit"]){
                break;
            }

            // create a new row and the cells for the username, place, power
            var user_row = document.createElement("tr");
            var name_div = document.createElement("td");
            var place_div = document.createElement("td");
            var power_div = document.createElement("td");

            name_div.textContent = user[0];
            place_div.textContent = user[1];
            power_div.textContent = user[2];

            user_row.className = "player-row";
            name_div.className = "player";
            place_div.className = "player-place";
            power_div.className = "player-power";

            name_div.setAttribute("tier", tier_name);
            place_div.setAttribute("tier", tier_name);
            power_div.setAttribute("tier", tier_name);

            tier_table.appendChild(user_row);
            user_row.appendChild(name_div);
            user_row.appendChild(place_div);
            user_row.appendChild(power_div);

            // add the users results
            for(var j=0; j<num_categories; j++){
                const time = user[j+3];

                var div = document.createElement("td");
                div.textContent = format(time);
                user_row.appendChild(div);

                const t = result_tier(j, time);

                // tier is -1 if below the first rank
                if(t != -1){
                    const name = tiers[t]["name"].toLowerCase();
                    div.setAttribute("tier", name);
                }
            }

            next_user++;
        }
    }
}

export function show_results_from_date(date){
    if(date in data){
        const str = decompress(data[date]);
        const table = JSON.parse(str);
        populate_table(table);

        // show the selected date on the button
        var date_button = document.getElementById("date-button");
        date_button.innerHTML = date;
    }
}

// show the latest results
var dates = Object.keys(data);
var latest = dates[dates.length-1];
show_results_from_date(latest);
