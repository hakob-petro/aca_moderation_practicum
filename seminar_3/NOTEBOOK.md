# Run Missions 3 and 4 in Jupyter on Modal

[missions_3_4.ipynb](missions_3_4.ipynb) is a guided version of the two mission
cards. You inspect tokens and logits, write the Yes/No scoring calculation,
try your own comments, calculate AUC by hand, score the dev split, and plot
ROC curves. The notebook exports the same files as the terminal route, so
the existing checks and Seminar 4 still work.

The notebook runs inside **JupyterLab on a Modal GPU**. Your laptop only
needs a browser. You do not need to install Jupyter or PyTorch on the class
server or your laptop. Modal's separate hosted notebook editor has been
[retired](https://modal.com/docs/guide/notebooks); this launcher uses
[Modal's Jupyter tunnel integration](https://modal.com/docs/guide/tunnels).

## Start from the class server

Finish Mission 1's Modal account setup first. Use your existing account or
the class profile already configured for you; do not replace the class token.

```bash
ssh ws
cd ~/course
git pull
uv tool upgrade modal
modal profile current
cd seminar_3
modal run notebook.py
```

The launcher needs Modal 1.5.5 or newer. The first launch builds an image and
may take several minutes. It then prints an HTTPS link ending in
`/lab/tree/missions_3_4.ipynb?token=...`. **Open the entire link on your
laptop.** Keep the launch terminal open. No SSH port forwarding is needed.
The link includes the session's access token; do not share it.

The default GPU is a T4. If it is unavailable, cancel the waiting launch and
use `modal run notebook.py --gpu L4` or `--gpu A10`. The notebook selects the
appropriate numerical precision for the GPU. Results can differ slightly.

## Work through the notebook

Run cells from top to bottom with **Shift+Enter**. Three **Your turn** cells
ask you to write the two scoring expressions, at least five comments of your
own, and the answer to the five-comment AUC exercise. These intentionally
stop until you fill them in. Read each explanation before running its cell.

The model loads once and is reused for both missions. The notebook also runs
`check 3` and `check 4` inside Modal. An error such as “Fill in both
expressions” or “Write at least five comments” is an exercise prompt: edit
that cell and rerun it, then continue.

Files in `~/s3` **inside this notebook are on Modal**, not yet on the class
server. The launcher stores them and the notebook in a persistent Modal
volume. Its name is printed in the terminal.

## Export and stop

1. Run the final **Export your mission files** cell. It reruns both checks,
   writes `notebook-results.zip`, and commits it to the volume.
2. Save the notebook with **Ctrl+S** or **Cmd+S**. Wait until its saving
   indicator clears.
3. Return to the class-server terminal that launched the notebook and press
   **Ctrl+C**. Wait for Modal to finish stopping the app.
4. In that same account and Modal profile, download the exported files:

   ```bash
   cd ~/course/seminar_3
   modal run notebook.py --download
   ./check 3
   ./check 4
   ```

The downloader restores `m3.txt`, `m4.txt`, `my_comments.txt`, `my_scores.tsv`,
`baseline.json`, `baseline_predictions.csv`, and the two split files under
`~/s3`. Different existing versions are backed up under
`~/s3/notebook-backups/` before replacement. Mission 2's other files remain
available. For example, the notebook does not replace your `m2.txt` answers.

Write your baseline AUC on the board. Seminar 4 can now use the downloaded
train/dev split and baseline.

**The GPU is billed while Jupyter is running, including idle time.** Closing
the browser tab does not stop it. The default session limit is 90 minutes;
`--minutes 60` changes it, up to a maximum of 120. If your SSH connection
disappears, check [Modal Apps](https://modal.com/apps) and stop your running
`aca-s3-notebook` app if necessary. Do not use `--detach` for the class exercise.

## Resume or change machines

Run the same launch command again. Your saved notebook and files remain, but
Python variables from a stopped kernel do not: rerun the setup and earlier
cells before continuing.

By default, the volume name is based on the username on the machine running
the launcher. To use a stable name across your laptop and the class server,
choose your own GitHub username on **both** commands:

```bash
modal run notebook.py --student YOUR_GITHUB_USERNAME
modal run notebook.py --download --student YOUR_GITHUB_USERNAME
```

Use the same Modal workspace/profile on both machines. Choose a distinct
student name when sharing the class workspace, and run only one session for
that name at a time.

The seed notebook is copied only on the first launch so a restart does not
overwrite your edits. If the course notebook is updated, keep your old copy
and open the new version in a new workspace name, or upload the updated
`.ipynb` using JupyterLab's file browser.

For a local copy of the edited notebook itself, save it, right-click its name
in JupyterLab's file browser, and choose **Download**. The mission export
contains the eight course files, not the notebook.

## Troubleshooting

| Symptom | What to do |
|---|---|
| No `modal` command | Complete Mission 1; install with `uv tool install modal`. |
| Error mentioning `with_options` | Run `uv tool upgrade modal` in the account launching it. |
| Authentication or billing error | Check `modal profile current` and your Mission 1 setup. |
| Link no longer connects | The app stopped or reached its time limit. Launch it again and use the new link. |
| GPU runs out of memory | Restart the kernel, rerun cells in order, and lower `score_chats`'s `batch_size` from 16 to 8. |
| “No export yet” when downloading | Open the same workspace, complete both checks, and run the final export cell. |
| A downloaded check fails | Read its hint, fix the notebook, rerun scoring and export, stop, then download again. |

For the scoring concepts and experimental findings, see
[Evaluating our moderation model](../materials/seminar_3/yes_no_scores_and_auc.md).
