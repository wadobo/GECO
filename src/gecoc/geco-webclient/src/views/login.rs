use yew::html::Html;
use yew::html::InputData;
use updater::Msg;
use model::Model;

use views::header;
use views::msgs;

pub fn view(model: &Model) -> Html<Msg> {
    html! {
        <div id="login", class="container",>
            { header::view("Login", model) }
            { msgs::error(&model.login.error) }

            <div class="row", >
                <div class="col-sm", ></div>
                <div class="col-sm", >
                    <div class="form-group", >
                        <input class="form-control", type="text", placeholder="username", oninput=|e: InputData| Msg::LoginSetUserName(Some(e.value)), />
                    </div>
                    <div class="form-group", >
                        <input class="form-control", type="password", placeholder="password", oninput=|e: InputData| Msg::LoginSetPassword(Some(e.value)), />
                    </div>
                    <button class="btn", class="btn-primary", onclick=|_| Msg::Login, >{ "Login" }</button>
                </div>
                <div class="col-sm", ></div>
            </div>
        </div>
    }
}

