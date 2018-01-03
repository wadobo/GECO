#[macro_use]
extern crate yew;
#[macro_use]
extern crate serde_json;

mod model;
mod updater;
mod views;

use yew::html::App;
use updater::update;
use updater::Context;
use model::Model;

fn main() {
    let model = Model::new();
    let mut app = App::new();
    let context = Context::new(&mut app);
    app.run(context, model, update, views::main);
}
