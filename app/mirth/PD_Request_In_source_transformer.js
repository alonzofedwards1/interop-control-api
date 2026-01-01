// Source Transformer script for PD_Request_In channel
var rawBody = "";
try {
    var data = connectorMessage.getRawData();
    if (data !== null && data !== undefined) {
        rawBody = String(data);
    }
} catch (e) {
    rawBody = "";
}

function respondWithBadRequest(message) {
    channelMap.put('error', message);
    responseMap.put('HTTP_STATUS', '400');
    responseMap.put('RESPONSE_BODY', message);
}

if (rawBody.trim().length === 0) {
    respondWithBadRequest('Empty request body');
    return;
}

var parsed;
try {
    parsed = JSON.parse(rawBody);
} catch (e) {
    respondWithBadRequest('Invalid JSON');
    return;
}

var patientReference = parsed['patient_reference'];
if (!patientReference) {
    respondWithBadRequest('Missing patient_reference');
    return;
}

var correlationId = null;
// Prefer header, then payload, then fallback UUID
var headers = sourceMap.get('requestHeaders');
if (headers) {
    var headerKeys = headers.keySet().toArray();
    for each (var key in headerKeys) {
        if (String(key).toLowerCase() === 'x-correlation-id') {
            var values = headers.get(key);
            if (values && values.size() > 0) {
                correlationId = String(values.get(0));
                break;
            }
        }
    }
}

if (!correlationId && parsed['correlation_id']) {
    correlationId = String(parsed['correlation_id']);
}

if (!correlationId) {
    correlationId = Packages.java.util.UUID.randomUUID().toString();
}

// Use provided callback URL or fall back to the shared test callback
var callbackUrl = parsed['callback_url'];
if (!callbackUrl || String(callbackUrl).trim().length === 0) {
    callbackUrl = 'http://100.27.251.103:8000/api/pd/callback';
}

channelMap.put('patient_reference', patientReference);
channelMap.put('correlation_id', correlationId);
channelMap.put('callback_url', callbackUrl);

responseMap.put('HTTP_STATUS', '202');
responseMap.put('RESPONSE_BODY', 'Accepted');
