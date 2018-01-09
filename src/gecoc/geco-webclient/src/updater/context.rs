use yew::html::App;
use yew::format::Json;
use yew::services::console::ConsoleService;
use yew::services::fetch::FetchService;
use yew::services::storage::{StorageService, Scope};

use updater::msg::Msg;

use model::Model;

pub const KEY: &'static str = "geco.model";

pub struct Context {
    pub console: ConsoleService,
    pub web: FetchService<Msg>,
    pub storage: StorageService,
}

impl Context {
    pub fn new(app: &mut App<Msg>) -> Context {
        Context {
            console: ConsoleService,
            web: FetchService::new(app.sender()),
            storage: StorageService::new(Scope::Local),
        }
    }

    pub fn get_model(&mut self) -> Model {
        if let Json(Ok(restored_model)) = self.storage.restore(KEY) {
            restored_model
        } else {
            Model::new()
        }
    }
}
