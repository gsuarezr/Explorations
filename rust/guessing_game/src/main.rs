use std::io;

fn main() {
    println!("Guess a number cara e chimba");
    let mut guess =Sring::new();
    io::stdin()
	.read_line(&mut guess)
	.expect("Failed to read line");
    println!("You guessed: {}",guess);
}
