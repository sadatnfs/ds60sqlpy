import JourneyCore

var plan = try StudyPlan()
try plan.add(StudyItem(id: "read", title: "Read the state chapter"))
try plan.add(StudyItem(id: "practice", title: "Build an independent example"))
try plan.update(id: "read", title: "Read the state chapter", completed: true)
let restored = try StudyPlan.decode(plan.encoded())
precondition(restored == plan)
precondition(restored.completedCount == 1)
print("JourneyCore: 1/2 complete; round trip passed")
