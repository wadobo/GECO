use yew::html::Html;
use updater::Msg;
use model::Model;
use model::PassModel;

use views::header;
use views::msgs;

pub fn view(model: &Model) -> Html<Msg> {
    html! {
        <div class="container",>
            { header::view("GECO", model) }
            { msgs::error(&model.error) }
            { msgs::info(&model.info) }

            <div class="passwords", >
                { for model.list.passwords.iter()
                        .zip(model.list.passwords.iter().skip(1))
                        .enumerate()
                        .filter(|x| x.0 % 2 == 0)
                        .map(passwd_row) }
            </div>
        </div>
    }
}

fn passwd_row(row: (usize, (&PassModel, &PassModel))) -> Html<Msg> {
    let pass = row.1;
    let i = row.0;

    html! {
        <div class="password", class="row", >
            { password_item(pass.0, i) }
            { password_item(pass.1, i + 1) }
        </div>
    }
}

fn password_item(pass: &PassModel, i: usize) -> Html<Msg> {
    let id = format!("passwd-{}", i);
    let target = format!("#{}", &id);

    html! {
        <div class="col-md-6",>
            <button class="btn", class="btn-primary", class="btn-block",
                    type="button", data-toggle="collapse", data-target={ &target },
                    aria-expanded="false", aria-controls="collapseExample",>
                { &(pass.name) }
            </button>

            <div class="collapse", id={id}, >
                <div class="card", class="card-body",>
                    { "Anim pariatur cliche reprehenderit, enim eiusmod high life accusamus terry richardson ad squid. Nihil anim keffiyeh helvetica, craft beer labore wes anderson cred nesciunt sapiente ea proident. "}
              </div>
        </div>
    }
}
