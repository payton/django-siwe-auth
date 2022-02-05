import WalletConnect from '@walletconnect/web3-provider';
import { ethers } from 'ethers';
import Mousetrap from 'mousetrap';
import { SignatureType, SiweMessage } from 'siwe';

declare global {
    interface Window {
        ethereum: { request: (opt: { method: string }) => Promise<Array<string>> };
        web3: unknown;
    }
}

const enum Providers {
    METAMASK = 'metamask',
    WALLET_CONNECT = 'walletconnect',
}

//eslint-disable-next-line
const metamask = window.ethereum;
let walletconnect: WalletConnect;

let toggleSize: HTMLButtonElement;
let closeButton: HTMLButtonElement;
let disconnectButton: HTMLDivElement;
let saveButton: HTMLDivElement;
let notepad: HTMLTextAreaElement;
let unsaved: HTMLParagraphElement;

let notepads: Array<[string, HTMLButtonElement]>;
let signInButton: HTMLButtonElement;

let warningWindow: HTMLDivElement;

/**
 * We need these to remove/add the eventListeners
 */

const signIn = async (connector: Providers) => {
    let provider: ethers.providers.Web3Provider;

    /**
     * Connects to the wallet and starts a etherjs provider.
     */
    if (connector === 'metamask') {
        await metamask.request({
            method: 'eth_requestAccounts',
        });
        provider = new ethers.providers.Web3Provider(metamask);
    } else {
        /**
         * The Infura ID provided just for the sake of the demo, you'll need to replace
         * it if you want to go to production.
         */
        walletconnect = new WalletConnect({
            infuraId: '8fcacee838e04f31b6ec145eb98879c8',
        });
        walletconnect.enable();
        provider = new ethers.providers.Web3Provider(walletconnect);
    }

    const [address] = await provider.listAccounts();
    if (!address) {
        throw new Error('Address not found.');
    }

    /**
     * Gets a nonce from our backend, this will add this nonce to the session so
     * we can check it on sign in.
     */
    const nonce = await fetch('/api/auth/nonce', {
        method: 'GET',
        credentials: 'include',
        headers: {
            X_CSRFToken: document.cookie.match(new RegExp('(^| )csrftoken=([^;]+)'))[2],
        },
    }).then((res) =>
        res.json().then((body) => body['nonce']),
    );

    /**
     * Creates the message object
     */
    const message = new SiweMessage({
        domain: document.location.host,
        address,
        chainId: parseInt(`${await provider.getNetwork().then(({ chainId }) => chainId)}`),
        uri: document.location.origin,
        version: '1',
        statement: 'Windows Ninety Eth Example',
        type: SignatureType.PERSONAL_SIGNATURE,
        nonce,
    });

    /**
     * Generates the message to be signed and uses the provider to ask for a signature
     */
    const signature = await provider.getSigner().signMessage(message.signMessage());

    /**
     * Calls our sign_in endpoint to validate the message, if successful it will
     * save the message in the session and allow the user to store his text
     */
    fetch(`/api/auth/login`, {
        method: 'POST',
        body: JSON.stringify({ message, signature }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.cookie.match(new RegExp('(^| )csrftoken=([^;]+)'))[2],
        },
        credentials: 'include',
    }).then(async (res) => {
        if (res.status === 200) {
            fetch('/api/me', { credentials: 'include' }).then((res) => {
                if (res.status === 200) {
                    res.json().then(({ text, address, ens }) => {
                        connectedState(text, ens ?? address);
                    });
                }
                return;
            });
        } else {
            res.json().then((err) => {
                console.error(err);
            });
        }
    });
};

const signOut = async () => {
    const loginElements = document.getElementsByClassName('login-screen');
    Array.prototype.forEach.call(loginElements, function (e: HTMLElement) {
        e.classList.remove('hidden');
    });

    const desktopElements = document.getElementsByClassName('desktop-screen');
    Array.prototype.forEach.call(desktopElements, function (e: HTMLElement) {
        e.classList.add('hidden');
    });
    updateTitle('Untitled');
    updateNotepad('');
    return fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.cookie.match(new RegExp('(^| )csrftoken=([^;]+)'))[2],
        },
    }).then(() => disconnectedState());
};

/**
 * Saves the current content of our notepad
 */
const save = async (e?: Mousetrap.ExtendedKeyboardEvent | MouseEvent) => {
    e?.preventDefault();
    const text = notepad.value;
    if (Buffer.byteLength(JSON.stringify({ text })) > 43610) {
        alert('Your message is too big.');
        return;
    }
    let activeNotepad = '';
    for (const n of notepads) {
        if (n[1].classList.contains('active-app')) {
            activeNotepad = n[0];
            break;
        }
    }
    return fetch('/api/save', {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, name: activeNotepad }),
    }).then(() => blockSave());
};

document.addEventListener('DOMContentLoaded', () => {
    /**
     * Try to fetch user information and updates the state accordingly
     */
    fetch('/api/me', { credentials: 'include' }).then((res) => {
        if (res.status === 200) {
            res.json().then(({ text, address, ens }) => {
                connectedState(text, ens ?? address);
            });
        } else {
            /**
             * No session we need to enable signIn buttons
             */
            const loginElements = document.getElementsByClassName('login-screen');
            Array.prototype.forEach.call(loginElements, function (e: HTMLElement) {
                e.classList.remove('hidden');
            });

            const desktopElements = document.getElementsByClassName('desktop-screen');
            Array.prototype.forEach.call(desktopElements, function (e: HTMLElement) {
                e.classList.add('hidden');
            });
            disconnectedState();
        }
    });

    /**
     * Bellow here are just helper functions to manage app state
     */
    disconnectButton = document.getElementById('disconnectButton') as HTMLDivElement;
    toggleSize = document.getElementById('toggleSize') as HTMLButtonElement;
    saveButton = document.getElementById('saveButton') as HTMLDivElement;
    notepad = document.getElementById('notepad') as HTMLTextAreaElement;
    closeButton = document.getElementById('closeButton') as HTMLButtonElement;
    unsaved = document.getElementById('unsaved') as HTMLParagraphElement;

    /**
     * Group buttons
     */
    notepads = [
        ['personal', document.getElementById('personalNotepad') as HTMLButtonElement],
        ['ens', document.getElementById('ensNotepad') as HTMLButtonElement],
        ['zorb', document.getElementById('zorbNotepad') as HTMLButtonElement],
        ['cryptoBaristas', document.getElementById('cryptoBaristasNotepad') as HTMLButtonElement],
    ];
    notepads.forEach((value, index) => {
        value[1].addEventListener(
            'click',
            function () {
                selectNotepad(index);
            },
            false,
        );
    });
    signInButton = document.getElementById('signIn') as HTMLButtonElement;

    warningWindow = document.getElementById('warningWindow') as HTMLDivElement;

    signInButton.addEventListener('click', () => {
        const selection = document.getElementById('selectProvider') as HTMLSelectElement;

        if (selection.value == 'metamask') {
            signIn(Providers.METAMASK).then(() => {
                void 0;
            });
        } else if (selection.value == 'wallet-connect') {
            signIn(Providers.WALLET_CONNECT).then(() => {
                void 0;
            });
        } else {
            console.log('Provider not yet supported.');
        }
    });

    toggleSize.addEventListener('click', maximize);
    disconnectButton.addEventListener('click', signOut);
    saveButton.addEventListener('click', save);
    notepad.addEventListener('input', enableSave);
});

const blockSave = () => {
    saveButton.removeEventListener('click', save);
    saveButton.setAttribute('disabled', 'true');
    updateUnsavedChanges('');
    window.onbeforeunload = null;
};

const enableSave = () => {
    saveButton.addEventListener('click', save);
    saveButton.removeAttribute('disabled');
    updateUnsavedChanges('- (***Unsaved Changes***)');
    window.onbeforeunload = () => '(***Unsaved Changes***)';
};

Mousetrap.bind('mod+s', save);

const connectedState = (text: string, title: string) => {
    const loginElements = document.getElementsByClassName('login-screen');
    Array.prototype.forEach.call(loginElements, function (e: HTMLElement) {
        e.classList.add('hidden');
    });

    const desktopElements = document.getElementsByClassName('desktop-screen');
    Array.prototype.forEach.call(desktopElements, function (e: HTMLElement) {
        e.classList.remove('hidden');
    });

    /**
     * Updates fields and buttons
     */
    closeButton.addEventListener('click', signOut);
    closeButton.removeAttribute('disabled');
    saveButton.classList.remove('hidden');
    disconnectButton.classList.remove('hidden');

    resetApps();

    /**
     * First notepad in list is active notepad on app start
     */
    notepads[0][1].classList.add('active-app');

    for (const n of notepads) {
        n[1].classList.remove('hidden');
    }

    if (text) {
        updateNotepad(text);
    }
    blockSave();
    updateTitle(title);
};

const disconnectedState = () => {
    closeButton.removeEventListener('click', signOut);
    closeButton.setAttribute('disabled', 'disabled');
    saveButton.classList.add('hidden');
    disconnectButton.classList.add('hidden');

    enableNotepad();
    resetApps();
    notepads.forEach((value, index) => {
        value[1].classList.add('hidden');
        if (value[1].getAttribute('listener') == 'true') {
            value[1].removeEventListener(
                'click',
                function () {
                    selectNotepad(index);
                },
                false,
            );
            value[1].setAttribute('listener', 'false');
        }
    });
};

const updateTitle = (text: string) => (document.getElementById('title').innerText = text);

const updateUnsavedChanges = (text: string) => (unsaved.innerText = text);

const updateNotepad = (text: string) => (notepad.value = text);

const disableNotepad = () => (notepad.disabled = true);

const enableNotepad = () => (notepad.disabled = false);

const maximize = () => {
    toggleSize.removeEventListener('click', maximize);
    toggleSize.addEventListener('click', restore);
    toggleSize.ariaLabel = 'Restore';
    notepad.style.width = '99.7vw';
    notepad.style.height = '91.7vh';
};

const restore = () => {
    toggleSize.removeEventListener('click', restore);
    toggleSize.addEventListener('click', maximize);
    toggleSize.ariaLabel = 'Maximize';
    notepad.style.width = '460px';
    notepad.style.height = '320px';
};

const resetApps = () => {
    notepads.forEach((value, index) => {
        value[1].classList.remove('active-app');
    });
};

const selectNotepad = (index: number) => {
    console.log('Calling selectNotepad from: ' + index);
    resetApps();
    const name = notepads[index][0];
    notepads[index][1].classList.add('active-app');

    if (name == 'personal') {
        fetch('/api/me', { credentials: 'include' }).then((res) => {
            if (res.status === 200) {
                res.json().then(({ text, address, ens }) => {
                    enableNotepad();
                    hideWarning();
                    if (text) {
                        updateNotepad(text);
                    } else {
                        updateNotepad(text);
                    }
                    blockSave();
                    updateTitle(ens ?? address);
                });
            } else {
                disableNotepad();
                updateNotepad('');
                blockSave();
                updateTitle(name);
                showWarning();
            }
            return;
        });
    } else {
        console.log('Fetching shared');
        fetch('/api/shared?name=' + name).then((res) => {
            if (res.status === 200) {
                res.json().then(({ text, address, ens }) => {
                    enableNotepad();
                    hideWarning();
                    if (text) {
                        updateNotepad(text);
                    } else {
                        updateNotepad('');
                    }
                    blockSave();
                    updateTitle(name);
                });
            } else {
                disableNotepad();
                updateNotepad('');
                blockSave();
                updateTitle(name);
                showWarning();
            }
            return;
        });
    }
};

const showWarning = () => {
    warningWindow.classList.remove('hidden');
    document.getElementById('closeWarningButton').addEventListener('click', hideWarning);
};

const hideWarning = () => {
    warningWindow.classList.add('hidden');
    document.getElementById('closeWarningButton').removeEventListener('click', hideWarning);
};
