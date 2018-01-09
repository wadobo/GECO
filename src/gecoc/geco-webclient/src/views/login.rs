use yew::html::Html;
use yew::html::InputData;
use updater::Msg;
use model::Model;

use views::header;
use views::msgs;

pub fn view(model: &Model) -> Html<Msg> {
    html! {
        <div id="login", class="container",>
            { header::view("GECO", model) }

            <div class="row", >
                <div class="col-sm", >
                    <h2>{"Login"}</h2>
                    { login(model) }
                </div>
                <div class="col-sm", >
                    <h2>{"Register"}</h2>
                    { register(model) }
                </div>
            </div>
        </div>
    }
}

pub fn login(model: &Model) -> Html<Msg> {
    html! {
        <div class="login", >
            { msgs::error(&model.login.error) }
            <div class="form-group", >
                <input class="form-control", type="text", placeholder="username", oninput=|e: InputData| Msg::LoginSetUserName(Some(e.value)), />
            </div>
            <div class="form-group", >
                <input class="form-control", type="password", placeholder="password", oninput=|e: InputData| Msg::LoginSetPassword(Some(e.value)), />
            </div>
            <button class="btn", class="btn-primary", onclick=|_| Msg::Login, >{ "Login" }</button>
        </div>
    }
}

pub fn register(model: &Model) -> Html<Msg> {
    html! {
        <div class="register", >
            { msgs::error(&model.register.error) }
            <div class="form-group", >
                <input class="form-control", type="text", placeholder="username", oninput=|e: InputData| Msg::RegisterUserName(Some(e.value)), />
            </div>
            <div class="form-group", >
                <input class="form-control", type="password", placeholder="password", oninput=|e: InputData| Msg::RegisterPassword(Some(e.value)), />
            </div>
            <div class="form-group", >
                <input class="form-control", type="password", placeholder="repeat password", oninput=|e: InputData| Msg::RegisterRepeat(Some(e.value)), />
            </div>
            <button class="btn", class="btn-primary", onclick=|_| Msg::Register, >{ "Register" }</button>
        </div>
    }
}
