<!--
 Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 -->

# What is the "declarations" folder for?

This "declarations" folder exists to fix broken TypeScript type definitions for the Apache Arrow project.

The apache-arrow 0.17.0 npm package fails to compile in modern TypeScript. The issue is tracked here: https://issues.apache.org/jira/browse/ARROW-8394

As a workaround, we provide a patched set of Arrow type declarations in this folder.

These are the changes:

- Copy the entirety of `./node_modules/apache-arrow` into `./declarations/apache-arrow`
- Delete all non `.d.ts` files, except for `package.json`, from the copied directory:
  ```
  $ find declarations/apache-arrow ! -name "*d.ts" -and ! -name "package.json" -type f -delete
  ```
- Add a `// @ts-nocheck` comment to the top of the declaration files that cause errors:
  - `declarations/apache-arrow/column.d.ts`
  - `declarations/apache-arrow/ipc/reader.d.ts`
  - `declarations/apache-arrow/recordbatch.d.ts`
- Add the following bits to `tsconfig.json`:
  ```
  "compilerOptions": {
    "paths": {
      "*": [
        "./*",
        "../declarations/*"
      ]
    }
  }
  ```

When apache-arrow is fixed, we should back out these changes!
