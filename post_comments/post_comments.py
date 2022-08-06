#!/usr/bin/env python3

# clang-tidy review - post comments
# Copyright (c) 2022 Peter Hill
# SPDX-License-Identifier: MIT
# See LICENSE for more information

import argparse
import pprint

from clang_tidy_review import *


def main(
    repo: str,
    token: str,
    max_comments: int,
    lgtm_comment_body: str,
    dry_run: bool,
) -> None:
    metadata: Metadata = load_metadata()
    print(f"Metadata: {metadata}")
    pull_request = PullRequest(repo, metadata["pr_number"], token)
    diff = pull_request.get_pr_diff()
    print(f"\nDiff from GitHub PR:\n{diff}\n")

    review = load_review()
    print(
        "clang-tidy-review generated the following review",
        pprint.pformat(review, width=130),
        flush=True,
    )

    if review["comments"] == []:
        print("No warnings to report, LGTM!")
        if not dry_run:
            pull_request.post_lgtm_comment(lgtm_comment_body)
        return

    print(f"::set-output name=total_comments::{len(review['comments'])}")

    print("Removing already posted or extra comments", flush=True)
    trimmed_review = cull_comments(pull_request, review, max_comments)

    if trimmed_review["comments"] == []:
        print("Everything already posted!")
        return

    if dry_run:
        pprint.pprint(review, width=130)
        return

    if not dry_run:
        print("Posting the review:\n", pprint.pformat(trimmed_review), flush=True)
        pull_request.post_review(trimmed_review)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Post a review based on feedback generated by the clang-tidy-review action"
    )

    add_shared_arguments(parser)

    parser.add_argument(
        "--dry-run", help="Run and generate review, but don't post", action="store_true"
    )

    args = parser.parse_args()

    main(
        repo=args.repo,
        token=args.token,
        max_comments=args.max_comments,
        lgtm_comment_body=strip_enclosing_quotes(args.lgtm_comment_body),
        dry_run=args.dry_run,
    )
