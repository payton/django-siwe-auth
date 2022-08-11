import { ethers } from 'ethers';
import { SiweMessage } from 'siwe';

const domain = window.location.host;
const origin = window.location.origin;
const provider = new ethers.providers.Web3Provider(window.ethereum);
const signer = provider.getSigner();

async function createSiweMessage(address, statement) {
    const res = await fetch(`/api/auth/nonce`, {
        credentials: 'include',
        headers: {
          'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
    });
    const nonce = (await res.json())['nonce'];
    const message = new SiweMessage({
        domain,
        address,
        statement,
        uri: origin,
        version: '1',
        chainId: '1',
        nonce: nonce
    });
    return message;
}

function connectWallet() {
    provider.send('eth_requestAccounts', [])
        .catch(() => console.log('user rejected request'));
}

async function signInWithEthereum() {
    await connectWallet();

    const message = await createSiweMessage(
        await signer.getAddress(),
        'Sign in with Ethereum to the app.'
    );
    const signature = await signer.signMessage(message.prepareMessage());

    const res = await fetch(`/api/auth/login`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        body: JSON.stringify({ message, signature }),
        credentials: 'include'
    });
    console.log(await res.text());
    location.reload();
}


const siweBtn = document.getElementById('siweBtn');
siweBtn.onclick = signInWithEthereum;
