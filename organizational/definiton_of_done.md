# Definition of Done
In this document, we want to define out definition of done, meaning all necessary steps to be fulfilled so that a feature of more generally speaking, a piece of code is considered done and ready to ship.

Version: 3a (08.12.2019, 18:20)

## Criteria
To be done, the following respective checklists have to be fully fulfilled.

---

## Requirements
- All functional requirements are met
- All non-functional requirements are met
- All acceptance criteria are met


### Code Quality
- Unit Tests have been written
- Tests are passing
- all `TODO:` annotations are resolved
- (peer) code review performed
- The code meets the criteria of the respective language specification checker with no ERRORS; this means in particular
    - `pycodequality` (formerly PEP8) for Python code, 
    - a tool like `JSLint` for JavaScript
    - the respective tools for other languages
- No unfinished or non-integrated work or work in progress is left over in code or environment
- Check that CI/CD is verified and working (as far as applicable)

### Documentation
- Any config or build changes are documented properly and at the correct place
- Documentation updated accordingly and at the proper locations
+ Backlog updated

#### Approval
- features are approved by Product Owner

#### Deployment
- Project is deployed to test environment (identical to production)
- All merge conflicts are resolved and the code is ready to be merged

---

## Changelog:
v3 -> v3a:
 - clarified definitian of ready to be merged (all conflicts are removed)

v2 -> v3:
 - Reformatted the File to reduce complexity
 - apply all the remaining criteria to all processes in the project
 - removed the following criteria in order to have a more realistic DoD:
 
 | Change   | Criteria                                 | Reason                                                            |
 |----------|------------------------------------------|-------------------------------------------------------------------|
 |-         | The project builds without errors        | As our project is script based, we have no direct build process!  |
 |-         | Tests for specific devices and/or platforms are created and passing | We currently are web only. Responsiveness is dealt with seperately |
 | -        | QA performed and issues are resolved     | No QA Department/Guidelines to follow.    |
 | -        | Backward Compatibility Tests Pass        | Not realistic.                            |
 | -        | Automated regression tests pass          | Not realistic at the moment.              |
 | -        | Integrated into Clean Build              | a) no builds and b) for now, not practically viable to rerun the crawler each time.   |
 | -        | OK from team                             | Responsibility delegated to Product Owner  |

