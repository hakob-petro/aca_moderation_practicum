"""The moderator console: an inbox, a review queue for a human, and the decision log.

Docker Compose starts it with `streamlit run app.py`. Streamlit runs this whole
script again after every click, so the state lives in the database, not here.
"""
import json
import random
from pathlib import Path

import streamlit as st

import decisions
import memory
from gateway_client import GatewayError
from pipeline import handle, signals

HERE = Path(__file__).resolve().parent
RULES = ["advertising", "legal"]
SHOWN = 3  # similar cases shown next to a comment

st.set_page_config(page_title="Moderator console", layout="wide")


@st.cache_data
def inbox():
    """Seminar 3's dev comments, in a fixed shuffled order. Their labels are not shown."""
    with open(HERE / "data" / "inbox.jsonl", encoding="utf-8") as lines:
        items = [json.loads(line) for line in lines]
    random.Random(6).shuffle(items)
    return items


con = decisions.connect()
mem = memory.load(con)


def process(source, rule, comment):
    result = handle(mem, rule, comment)
    result["id"] = decisions.record(con, source, rule, comment, result["gateway"], result["routed"],
                                    result["vote"], result["precedent"])
    return result


def fmt(value, pattern="{:.2f}"):
    return "–" if value is None else pattern.format(value)


def show_similar(similar):
    if not similar:
        st.caption("Similar past cases appear here after mission 2.")
        return
    for case in similar[:SHOWN]:
        verdict = "broke the rule" if case["label"] else "followed the rule"
        st.caption(f"similarity {case['similarity']:.2f} · {verdict} · from {case['source']}")
        st.text(case["comment"][:400])


def gateway_failed(error):
    st.error(f"No decision: {error}. If the model is cold, warm it with "
             "`uv run client.py` in ~/course/seminar_5, then try again.")


counts = decisions.counts(con)
st.title("Moderator console")
st.caption(f"{counts['logged']} decisions logged · {counts['waiting']} waiting for a human · "
           f"{counts['by_human']} decided by a human · {counts['overrides']} overrides")
inbox_tab, review_tab, log_tab = st.tabs(["Inbox", f"Review queue ({counts['waiting']})", "Decision log"])

with inbox_tab:
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Incoming comments")
        done = {(row["rule"], row["comment"]) for row in con.execute("SELECT rule, comment FROM decisions")}
        todo = [item for item in inbox() if (item["rule"], item["comment"]) not in done]
        st.write(f"{len(todo)} comments wait in the inbox. The gateway decides each one; "
                 "a **review** goes to the review queue.")
        if st.button("Moderate the next 5", disabled=not todo, type="primary"):
            batch = []
            for item in todo[:5]:
                try:
                    result = process("inbox", item["rule"], item["comment"])
                except GatewayError as error:
                    gateway_failed(error)
                    break
                batch.append({"#": result["id"], "rule": item["rule"], "comment": item["comment"][:100],
                              "p_yes": round(result["gateway"]["p_yes"], 3),
                              "model": result["gateway"]["decision"], "console": result["routed"],
                              "vote": fmt(result["vote"], "{:.0%}")})
            st.session_state["batch_result"] = batch
        if st.session_state.get("batch_result"):
            st.dataframe(st.session_state["batch_result"], hide_index=True)

    with right:
        st.subheader("Try a comment")
        with st.form("typed"):
            rule = st.selectbox("Rule", RULES)
            comment = st.text_area("Comment", max_chars=2000)
            submitted = st.form_submit_button("Moderate")
        if submitted and comment.strip():
            try:
                st.session_state["typed_result"] = process("typed", rule, comment)
            except GatewayError as error:
                gateway_failed(error)
        typed = st.session_state.get("typed_result")
        if typed:
            gateway = typed["gateway"]
            st.metric("p_yes", f"{gateway['p_yes']:.3f}")
            st.write(f"Model: **{gateway['decision']}** · console: **{typed['routed']}** · "
                     f"vote of the {memory.K} nearest: {fmt(typed['vote'], '{:.0%}')} · "
                     f"nearest removed case: {fmt(typed['precedent'])}")
            show_similar(typed["similar"])

with review_tab:
    waiting = decisions.pending(con)
    if not waiting:
        st.success("Nothing waits for a human.")
    for row in waiting[:20]:
        with st.container(border=True):
            st.caption(f"#{row['id']} · {row['rule']} · p_yes {fmt(row['p_yes'], '{:.3f}')} · "
                       f"model: {row['model_decision']} · vote {fmt(row['vote'], '{:.0%}')} · "
                       f"nearest removed case {fmt(row['precedent'])}")
            st.text(row["comment"])
            with st.expander("Similar past cases"):
                show_similar(signals(mem, row["rule"], row["comment"])["similar"])
            approve, remove, _ = st.columns([1, 1, 6])
            if approve.button("Approve", key=f"approve-{row['id']}"):
                decisions.set_final(con, row["id"], "approve")
                st.rerun()
            if remove.button("Remove", key=f"remove-{row['id']}"):
                decisions.set_final(con, row["id"], "remove")
                st.rerun()

with log_tab:
    rows = [dict(row) for row in decisions.recent(con)]
    st.dataframe(rows, hide_index=True, column_order=[
        "id", "source", "rule", "comment", "p_yes", "model_decision", "vote", "precedent",
        "routed", "final", "decided_by", "request_id"])
    st.subheader("Override a decision")
    with st.form("override"):
        decision_id = st.number_input("Decision #", min_value=1, step=1)
        final = st.radio("Final decision", ["approve", "remove"], horizontal=True)
        if st.form_submit_button("Override"):
            try:
                decisions.set_final(con, int(decision_id), final)
                st.success(f"Decision #{int(decision_id)} is now {final}, decided by a human.")
            except KeyError:
                st.error("No decision has that number.")
