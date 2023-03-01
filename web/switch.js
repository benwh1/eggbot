import { tiers } from "./data.js"

const tierlist = tiers.map(tier => tier.name.toLowerCase()).reverse()
const switchBtn = document.querySelector("#switch")

switchBtn.addEventListener("change", () => tierlist.forEach(tier => changeTable(tier)))

function changeTable(tier_table) {
    document.querySelectorAll(`#${tier_table}-table .player-row *`).forEach((element, i) => {
        const tier = element.getAttribute("tier")

        if (!tier) return;
        let tier_index = tierlist.indexOf(tier);
        let table_index = tierlist.indexOf(tier_table);
        if(table_index > tier_index) {
            element.style.fontWeight = switchBtn.checked ? 800 : "";
        } else if(table_index < tier_index) {
            element.style.backgroundColor = switchBtn.checked ? "grey" : "";
        }
    });
}
