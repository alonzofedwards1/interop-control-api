// ============================================================
// PD_Request_In — Destination Transformer (HTTP Sender)
// CONTROL PLANE OWNED AUTH
// ============================================================

/*
  Architecture rules:
  - OAuth handled by FastAPI
  - Authorization header already present
  - Mirth does NOT inject tokens
  - Mirth only observes outcomes
*/

/* ------------------------------------------------------------
 * 1. Read HTTP response from OpenEMR (POST-REQUEST)
 * ------------------------------------------------------------ */
var status = responseMap.get('status') || 0;   // HTTP status code (number) or 0 on failure
var body   = responseMap.get('body')   || '';  // response body (string)
var error  = responseMap.get('error');         // transport error details when connection fails
var statusMessage = responseMap.get('statusMessage') || responseMap.get('responseStatusMessage');

/* ------------------------------------------------------------
 * 2. Defaults
 * ------------------------------------------------------------ */
channelMap.put('pd_outcome', 'NO_MATCH');
channelMap.put('pd_status', 'ERROR');
channelMap.put('pd_http_status', status);

/* ------------------------------------------------------------
 * 3. Evaluate OpenEMR response
 * ------------------------------------------------------------ */
if (status === 200 && body.length > 0) {
    try {
        var json = JSON.parse(body);
        var patients = json.data || [];

        if (Array.isArray(patients) && patients.length > 0) {
            channelMap.put('pd_outcome', 'AA');   // Match
            channelMap.put('pd_status', 'MATCH');
            channelMap.put('patient_id', patients[0].id);
        } else {
            channelMap.put('pd_outcome', 'NF');   // Not Found
            channelMap.put('pd_status', 'NO_MATCH');
        }
    } catch (e) {
        channelMap.put('pd_error', 'Invalid JSON from OpenEMR');
    }
} else if (status === 0) {
    // Connection failure or no HTTP response
    var detail = error || statusMessage || 'No HTTP response from OpenEMR';
    channelMap.put('pd_error', detail);
} else {
    var suffix = statusMessage ? (' ' + statusMessage) : '';
    channelMap.put('pd_error', 'HTTP ' + status + suffix);
}
