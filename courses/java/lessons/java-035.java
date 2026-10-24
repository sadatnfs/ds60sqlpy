// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Verify the domain summary
        // SummarizegroupAoveramounts10,20 andgroupBover5.
        // Expected: Acount2,total30;Bcount1,total5.

        // Exercise 2: Read a successful HTTPsummary
        // GET/summary?group=Afromtheownedserver.
        // Expected: status200 andexactJSONwithcount2,total30.

        // Exercise 3: Report an unknown validgroup
        // GETgroupC,whichpasses syntax buthasnorecords.
        // Expected: status404 withnot_found error.

        // Exercise 4: Reject ambiguous ormalformedqueries
        // Sendduplicategroupparameters andalowercasegroup.
        // Expected: bothstatus400.

        // Exercise 5: Reject unsupportedmethods andpathlookalikes
        // POSTtothesummaryroute andGET/summary-extra.
        // Expected: 405 and404 respectively.

        // Exercise 6: Preserve storage andclose theownedlistener
        // Comparetherepositorybefore/afterrequests andclose theserver.
        // Expected: 3unchangedrecords;closedflagtrue.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
