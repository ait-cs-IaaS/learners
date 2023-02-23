import axios from "axios";
import { store } from "@/store";

axios.defaults.baseURL = "http://localhost:5000/";

let token = store.getters.getJwt;
if (token) axios.defaults.headers.common["Authorization"] = "Bearer " + token;
