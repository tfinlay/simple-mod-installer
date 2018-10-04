/*
* Various utilities which are shared between files on the frontend
*/
import {MdDialog, MdSnackBarConfig} from "@angular/material";

export let DEFAULT_SNACKBAR_CONFIG = new MdSnackBarConfig();
DEFAULT_SNACKBAR_CONFIG.duration = 15000;


export function getFilename(url: string): string {
    let filename = url.split("/")[-1];

    console.log("Found filename to be: " + filename);

    return filename;
}


export function stringifyArray(arr: any[]): string {
    let s = "";
    for (let x=0; x < arr.length; x++) {
        if (x == 0) {
            s += arr[x];
        } else {
            s += ", " + arr[x];
        }

    }

    return s;
}


export class ServerMessage {
    status: string;
    errInfo: ServerErrorMessage;
    success = false;

    data: any;

    constructor(data) {
        this.status = data.status;
        this.data = data;

        if (data.status === 'success') {
            this.success = true;
        } else {
            this.errInfo = {
                title: data.title,
                body: data.body,
                code: data.code
            };
        }
    }
}

export interface ServerErrorMessage {
    title: string;
    body: string;
    code: string;
}