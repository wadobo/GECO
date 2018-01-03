pub mod header;

pub mod msgs;
pub mod list;
pub mod login;

use model::Model;
use updater::Msg;
use yew::html::Html;

pub fn main(model: &Model) -> Html<Msg> {
    match model.login.token {
        Some(_) => list::view(model),
        None => login::view(model)
    }
}
