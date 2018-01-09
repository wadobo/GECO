use yew::html::Html;
use updater::Msg;
use model::Model;

pub fn view(title: &str, model: &Model) -> Html<Msg> {
    html! {
        <div id="header", class="row", >
            <div class="col",>
                <h1>{ title }</h1>
            </div>
            <div class="col-5", >
                <button class="btn", class="btn-light", class="float-right",
                        onclick=|_| Msg::Logout,>
                    { match model.login.token { Some(_) => "logout", None => "" } }
                </button>
            </div>
        </div>
    }
}
