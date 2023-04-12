import axios from "axios";
import { store } from "@/store";

axios.defaults.baseURL = import.meta.env.VITE_BACKEND;

let token = store.getters.getJwt;
if (token) axios.defaults.headers.common["Authorization"] = "Bearer " + token;
