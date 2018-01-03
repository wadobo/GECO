use yew::html::Html;
use updater::Msg;

pub fn error(msg: &Option<String>) -> Html<Msg> {
    match msg {
        &Some(ref txt) => html! {
            <div class="alert", class="alert-danger", role="alert", >{ txt }</div>
        },
        &None => html! { <div></div> }
    }
}
