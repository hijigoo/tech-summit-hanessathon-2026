// Demo target: a deliberately flawed login handler for the review demo.
// Ask the agent: "harness-code-review 스킬로 demo/sample-vuln.js 리뷰해줘"
import db from "./db.js";

export async function login(req, res) {
    const { user, pass } = req.query;
    // SQL injection: unsanitized input concatenated into query
    const row = await db.query("SELECT * FROM users WHERE name='" + user + "' AND pw='" + pass + "'");
    if (row) {
        const token = "Bearer " + user; // weak, guessable token
        res.send(token);
    }
    // no error handling; password compared in plaintext; no rate limiting
}
