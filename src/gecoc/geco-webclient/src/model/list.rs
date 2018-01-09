#[derive(Serialize, Deserialize)]
#[derive(Clone)]
pub struct PassModel {
    pub name: String,
    pub ptype: String,
    pub desc: String,
    pub account: String,
    pub password: String,
    pub cypher: String,
    pub updated: f64,
    pub expiration: f64,
}

#[derive(Serialize, Deserialize)]
pub struct ListModel {
    pub passwords: Vec<PassModel>,
}

impl ListModel {
    pub fn new() -> ListModel {
        ListModel {
            passwords: vec![],
        }
    }
}
