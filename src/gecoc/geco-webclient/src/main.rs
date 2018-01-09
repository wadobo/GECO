#[macro_use]
extern crate yew;
#[macro_use]
extern crate serde_json;
#[macro_use]
extern crate serde_derive;

mod model;
mod updater;
mod views;

use yew::html::App;
use updater::update;
use updater::Context;

fn main() {
    yew::initialize();
    let mut app = App::new();
    let mut context = Context::new(&mut app);
    let model = context.get_model();
    app.mount(context, model, update, views::main);
    yew::run_loop();
}
