players = ["eyew", "other-side"];
image_path = "static/images/";
bg_images = [image_path + "blurry_black_red.jpg", image_path + "blurry_blue.jpg"];
bg_colours = ["5e5151", "544361"]; // average colour of bg image
let current_player = 0;


function changePlayer(direction) {
    // TODO: Player should stop when function called
    document.getElementById(players[current_player]).classList.add('hide');
    if (direction === 'r') {
        current_player++;
    } else if (direction === 'l') {
        current_player--;
        if (current_player < 0) {
            current_player = players.length - 1;
        }
    }
    current_player %= players.length;
    document.getElementById('body').style.backgroundImage = 'url(' + bg_images[current_player] + ')';
    document.getElementById('body').style.backgroundColor = '#' + bg_colours[current_player];
    document.getElementById(players[current_player]).classList.remove('hide');
    console.log(current_player)
}
