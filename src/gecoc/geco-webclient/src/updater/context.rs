use yew::html::App;
use yew::services::console::ConsoleService;
use yew::services::fetch::FetchService;

use updater::msg::Msg;

pub struct Context {
    pub console: ConsoleService,
    pub web: FetchService<Msg>,
}

impl Context {
    pub fn new(app: &mut App<Msg>) -> Context {
        Context {
            console: ConsoleService,
            web: FetchService::new(app.sender()),
        }
    }
}
