const domain = "https://localhost:8443"
const options = {
    roomName: 'JitsiMeetAPIExample',
    parentNode: document.querySelector('#presentation')
};

api = new JitsiMeetExternalAPI(domain, options)
