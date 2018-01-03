use yew::html::Html;
use updater::Msg;
use model::Model;

use views::header;

pub fn view(model: &Model) -> Html<Msg> {
    html! {
        <div class="container",>
            { header::view("List", model) }
            <h1>{ "HOLA" }</h1>
        </div>
    }
}
