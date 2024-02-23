/*
A KBase module: kb_qsip
*/

module kb_qsip {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_qsip(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
