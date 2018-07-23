players = ["eyew", "other-side"];
image_path = "static/images/";
bg_images = [image_path + "blurry_black_red.jpg", image_path + "blurry_blue.jpg"];
bg_colours = ["5e5151", "544361"]; // average colour of bg image
let current_player = 0;

bandcamp_players = get_players();
hide_all_but_first('music-wrapper');

/**
 * Get all bandCamp players
 * @returns {HTMLCollection}
 */
function get_players() {
    return document.getElementById('music-wrapper').children;
}

function changePlayer(direction) {
    //hide current player
    bandcamp_players[current_player].classList.add('hide');
    //TODO: stop music playing from current player

    //find next player
    if (direction === 'r') {
        current_player++;
        current_player %= bandcamp_players.length;
    } else if (direction === 'l') {
        current_player--;
        if (current_player < 0) {
            current_player = bandcamp_players.length - 1;
        }
    }

    //show next player
    bandcamp_players[current_player].classList.remove('hide');
}


// function changePlayer(direction) {
//     TODO: Player should stop when function called
// document.getElementById(players[current_player]).classList.add('hide');
// if (direction === 'r') {
//     current_player++;
// } else if (direction === 'l') {
//     current_player--;
//     if (current_player < 0) {
//         current_player = players.length - 1;
//     }
// }
// current_player %= players.length;
// document.getElementById('body').style.backgroundImage = 'url(' + bg_images[current_player] + ')';
// document.getElementById('body').style.backgroundColor = '#' + bg_colours[current_player];
// document.getElementById(players[current_player]).classList.remove('hide');
// console.log(current_player)
// }

/**
 * Hide all iframes except the first one
 */
function hide_all_but_first(parent) {
    let musicWrap = document.getElementById(parent);
    let children = musicWrap.children;

    if (musicWrap.childElementCount <= 1) {
        let arrows = document.getElementsByClassName('arrow');
        for (let i = 0; i < arrows.length; i++) {
            arrows[i].classList.add('hide');
        }
        return;
    }

    for (let i = 1; i < musicWrap.childElementCount; i++) {
        children[i].classList.add('hide');
    }
}
