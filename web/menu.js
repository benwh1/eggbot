import("https://kit.fontawesome.com/9fa2f75402.js"); // font awesome icons

const menu = document.querySelector(".menu");
const menuIcon = document.querySelector(".menu-icon");

const menuToggle = () => {
    menu.classList.toggle("menu-active");
    menuIcon.classList.toggle("menu-icon-open");
    document.body.classList.toggle("overflow-hidden");
};

// when clicking outside the menu to close it
document.addEventListener( "click", () => menu.classList.contains("menu-active") && menuToggle());

document.querySelector(".menu-btn").addEventListener("click", e => {
    e.stopPropagation();
    menuToggle();
});

menu.addEventListener("click", e => e.stopPropagation());
