"""
PROTON
(C) 2022-2042, Kumar Madhukar
Department of Computer Science and Engineering, Indian Institute of Technology Delhi
"""

"""
Validates variant, invariant using testing
"""
# TODO is the ranking function > 0 check in place
import os
import os.path
import re
import subprocess

from tqdm import tqdm

import utils as u
from config import Config as c


import logging
l = logging.getLogger( __name__ )
l.setLevel( logging.DEBUG )


def add_braces( full_code ):
    """
    Adds braces to given code using the bracer bin. Returns a result. Failure
    reasons:
    
    BRACER  -   The bracer failed.
    """
    # Write code
    u.clear_tmp()
    with open( os.path.join( c.TMP_PATH, c.BRACER_IN_FNAME ), 'w') as f:
        f.write( full_code )

    bracer_res = subprocess.run( 
        args = [ 
            os.path.relpath( c.BRACER_PATH, c.TMP_PATH ),
            '-in', 
            c.BRACER_IN_FNAME,
        ],
        check = False,
        cwd = c.TMP_PATH,
    )
    
    # Check status
    if bracer_res.returncode != 0:
        msg = "Bracer failed"
        if c.IGNORE_EXTRACTOR_RET_CODE:
            l.warning( msg )
        else:
            l.error( msg )
            return u.Result( None, 'BRACER' )
    l.info( "Bracer succeeded")

    # Check c file exists
    out_fpath = os.path.join( c.TMP_PATH, c.BRACER_OUT_FNAME )
    if not os.path.exists(out_fpath):
        msg = "Bracer output does not exist. ".format( out_fpath )
        l.error( msg ) 
        return u.Result( None, 'BRACER' )

    # Load code
    with open( out_fpath, 'r' ) as f:
        braced_code = f.read()

    return u.Result( braced_code, None )


def validate_test( loop_data ):
    """
    Validate variant in loop_data via testing. 
    
    Returns: Status that is true if validation succeeded. Failure reasons may be:
    
    INSTRUMENTER    -   Instrumenter for adding asserts for validation
                        failed.
    COMPILATION     -   Failed to compile instrumented code
    TEST_ASSERT     -   Test runs failed - potentially due to assertion
                        violation
    TEST_TIMEOUT    -   Test runs timed out - 
    """
    # TODO Add check for invariant being positive 
    if c.ASSERTS:
        assert loop_data.variant is not None
        assert loop_data.invariant is not None
        assert loop_data.assigns is not None
        assert loop_data.loop_code is not None
        assert loop_data.full_code is not None
        assert loop_data.invariant is not None
        assert loop_data.loop_type is not None
        assert loop_data.variant is not None

    Ccondition = ""

    loop_code = loop_data.loop_code.strip() # Idk why we need strip, was from before
    full_code = loop_data.full_code
    loop_variant = loop_data.variant
    loop_type = loop_data.loop_type

    # Code to instrument with
    var_init = "int oldVal = 2147483647;"
    var_assert = "__IPROTON_test( " + loop_variant + " < oldVal);" + \
            "__IPROTON_test( " + loop_variant + " >= 0 );" + \
            "oldVal = " + loop_variant + ";" 

    l.debug("Loop variant: {}".format( loop_variant ))

    # Get index of start of loop
    if (loop_code in full_code):
        loop_start_idx = full_code.find(loop_code)
        # Get the index at the end of loop_code
        before_loop = full_code[:loop_start_idx]
        after_loop = full_code[loop_start_idx:]
    else:
        l.warning( "Couldn't find loop code in full code" )
        return u.Status( False, 'INSTRUMENTER' )

    # Mark start of loop
    loop_mark = "/* __IPROTON_LOOP_START__ */"
    loop_marked_code = before_loop + loop_mark + after_loop

    # Brace the code
    res = add_braces( loop_marked_code )
    if res.result is None:
        return u.Status( False, res.failure_reason )
    braced_code = res.result

    # Get back start of loop and pieces
    loop_start_idx = braced_code.find( loop_mark )
    if loop_start_idx == '-1':
        l.error( "Couldn't find loop start marker in braced code" )
        return u.Status( False, 'INSTRUMENTER' )
    before_loop = braced_code[:loop_start_idx]
    after_loop  = braced_code[loop_start_idx:]
    
    # Add initialization for variant
    code_with_init = before_loop + var_init + after_loop

    # Find beginning of loop keyword 
    if (loop_type == "WhileStmt"):
        loop_kwd_start = code_with_init.find("while", loop_start_idx)
    elif (loop_type == "ForStmt"):
        loop_kwd_start = code_with_init.find("for", loop_start_idx)
    elif (loop_type == "DoStmt"):
        loop_kwd_start = code_with_init.find("do", loop_start_idx)
    else:
        l.warning( "Loop has unkown loop type" )
        return u.Status( False, 'INSTRUMENTER' )
    l.debug( "Loop keyword at: {}".format( loop_kwd_start )) 
    if loop_kwd_start == -1:
        l.warning("loop keyword not found")
        return u.Status( False, 'INSTRUMENTER' )

    # l.debug("Index of 'while': {}".format( loop_kwd_start))
    body_start_index = code_with_init.find(
        "{", loop_kwd_start) + 1
    l.debug( "body_start: {}".format( body_start_index )) 
    if body_start_index == -1:
        l.warning("Brace not found after loop start")
        return u.Status( False, 'INSTRUMENTER' )
    before_body_start = code_with_init[:body_start_index]
    after_body_start = code_with_init[body_start_index:]
    instrumented_code = before_body_start + var_assert + after_body_start

    # Add headers
    instrumented_code = (
        """
            /* Instrumented for llm-ter-check */
            #include <time.h>
            #define __IPROTON_TEST_FAILED_ERRMSG "{0}"
            #define __IPROTON_TEST_FAILED_EXCODE {1}
            #include <{2}>
        """.format( 
                c.TEST_FAILED_ERRMSG, c.TEST_FAILED_EXCODE, c.INSTR_HEADER ) +
        instrumented_code 
    )

    # Add stub main with srand initialized from time
    instrumented_code = instrumented_code.replace( "main", "orig_main" )
    instrumented_code = instrumented_code + """
        int main() {
            srand( clock() ); // time(0) does not have enough resolution
            orig_main();
        }
    """

    # Write c code
    c_fpath = os.path.join( c.TMP_PATH, c.TEST_C_FNAME )
    bin_fpath = os.path.join( c.TMP_PATH, c.TEST_BIN_FNAME )
    with open( c_fpath, 'w' ) as f:
        f.write( instrumented_code )

    # Compile via gcc
    include_path = c.INCLUDES_DIR
    l.debug( "Include path: {}".format( include_path ))
    ret = subprocess.run(
        args = [ 
            'gcc', 
            '-I', include_path,
            '-o', bin_fpath, 
            c_fpath ],
        check = False,
    )
    if ret.returncode != 0:
        l.warning( "Failed to compile instrumented code" )
        return u.Status( False, 'COMPILATION' )
    l.debug( "Compilation succeeded" )

    # Run code
    for _ in tqdm( range( c.NUM_RUNS )):

        # Handle timeout
        try:
            l.debug( "Running bin" )
            ret = subprocess.run(
                args = [ bin_fpath ],
                check = False,
                timeout = c.RUN_TIMEOUT,
                capture_output = True,
                text = True,
            )

        # If timeout, assume terminates since assert not triggered
        except subprocess.TimeoutExpired:
            l.warning( "Run timed out" )
            if c.TEST_TO_CONSIDER_TERM:
                continue
            else: 
                return u.Status( False, 'TEST_TIMEOUT' )

        # If test failed
        if (    ret.returncode == c.TEST_FAILED_EXCODE and 
                c.TEST_FAILED_ERRMSG in ret.stderr          ):
            l.warning( "Assert failed" )
            return u.Status( False, 'TEST_ASSERT' )
        
        # Some other error, report and continue
        if ret.returncode != 0:
            l.warning( 
                "Running failed with return code {} stdout {} stderr {}".format( 
                    ret.returncode, ret.stdout, ret.stderr
            ))

    return u.Status( True, None )


def validate_cbmc( loop_data ):
    """
    Validate variant in loop_data via cbmc. 
    
    Returns: Status that is true if validation succeeded. Failure reasons may be:
    
    INSTRUMENTER    -   Instrumenter for adding asserts for validation
                        failed.
    CBMC_ASSERT     -   CBMC detected assertion violation
    CBMC_TIMEOUT    -   CBMC timed out 
    CBMC_ERROR      -   CBMC threw an error
    """
    # TODO Add check for invariant being positive 
    if c.ASSERTS:
        assert loop_data.variant is not None
        assert loop_data.invariant is not None
        assert loop_data.assigns is not None
        assert loop_data.loop_code is not None
        assert loop_data.full_code is not None
        assert loop_data.invariant is not None
        assert loop_data.loop_type is not None
        assert loop_data.variant is not None

    Ccondition = ""

    loop_code = loop_data.loop_code.strip() # Idk why we need strip, was from before
    full_code = loop_data.full_code
    loop_variant = loop_data.variant
    loop_type = loop_data.loop_type

    # Code to instrument with
    var_init = "int oldVal = 2147483647;"
    var_assert = """
        __CPROVER_assert( {0} < oldVal, "{1}" );
        __CPROVER_assert( {0} >= 0, "{2}" );
        oldVal = {0};
    """.format( loop_variant, c.CBMC_DEC_ASSERT, c.CBMC_POS_ASSERT )

    l.debug("Loop variant: {}".format( loop_variant ))

    # Get index of start of loop
    if (loop_code in full_code):
        loop_start_idx = full_code.find(loop_code)
        # Get the index at the end of loop_code
        before_loop = full_code[:loop_start_idx]
        after_loop = full_code[loop_start_idx:]
    else:
        l.warning( "Couldn't find loop code in full code" )
        return u.Status( False, 'INSTRUMENTER' )

    # Mark start of loop
    loop_mark = "/* __IPROTON_LOOP_START__ */"
    loop_marked_code = before_loop + loop_mark + after_loop

    # Brace the code
    res = add_braces( loop_marked_code )
    if res.result is None:
        return u.Status( False, res.failure_reason )
    braced_code = res.result

    # Get back start of loop and pieces
    loop_start_idx = braced_code.find( loop_mark )
    if loop_start_idx == '-1':
        l.error( "Couldn't find loop start marker in braced code" )
        return u.Status( False, 'INSTRUMENTER' )
    before_loop = braced_code[:loop_start_idx]
    after_loop  = braced_code[loop_start_idx:]
    
    # Add initialization for variant
    code_with_init = before_loop + var_init + after_loop

    # Find beginning of loop keyword 
    if (loop_type == "WhileStmt"):
        loop_kwd_start = code_with_init.find("while", loop_start_idx)
    elif (loop_type == "ForStmt"):
        loop_kwd_start = code_with_init.find("for", loop_start_idx)
    elif (loop_type == "DoStmt"):
        loop_kwd_start = code_with_init.find("do", loop_start_idx)
    else:
        l.warning( "Loop has unkown loop type" )
        return u.Status( False, 'INSTRUMENTER' )
    l.debug( "Loop keyword at: {}".format( loop_kwd_start )) 
    if loop_kwd_start == -1:
        l.warning("loop keyword not found")
        return u.Status( False, 'INSTRUMENTER' )

    # l.debug("Index of 'while': {}".format( loop_kwd_start))
    body_start_index = code_with_init.find(
        "{", loop_kwd_start) + 1
    l.debug( "body_start: {}".format( body_start_index )) 
    if body_start_index == -1:
        l.warning("Brace not found after loop start")
        return u.Status( False, 'INSTRUMENTER' )
    before_body_start = code_with_init[:body_start_index]
    after_body_start = code_with_init[body_start_index:]
    instrumented_code = before_body_start + var_assert + after_body_start

    # Add headers
    instrumented_code = (
        """
            /* Instrumented for llm-ter-check */
        """ +
        instrumented_code 
    )

    # Write c code
    c_fpath = os.path.join( c.TMP_PATH, c.TEST_C_FNAME )
    with open( c_fpath, 'w' ) as f:
        f.write( instrumented_code )

    # Call cbmc
    try :
        ret = subprocess.run(
            args = [  
                'cbmc',
                '--unwind', str(c.CBMC_NUM_UNWIND),
                '--z3',
                c_fpath,
            ],
            check = False,
            timeout = c.CBMC_TIMEOUT,
            capture_output = True,
            text = True,
        )

    # If timeout, assume terminates since assert not triggered
    except subprocess.TimeoutExpired:
        l.warning( "cbmc timed out" )
        if c.CBMC_TO_CONSIDER_TERM:
            return u.Status( True, None )
        else: 
            return u.Status( False, 'CBMC_TIMEOUT' )

    # Look at output for dec
    res_idx = ret.stdout.find( c.CBMC_DEC_ASSERT )
    if res_idx == -1:
        l.error( "CBMC did not have result" )
        return u.Status( False, 'CBMC_ERROR' )
    line_end_idx = ret.stdout.find( '\n', res_idx )
    res_str = ret.stdout[ res_idx : line_end_idx ]
    if c.CBMC_RES_PASS in res_str:
        l.info( "DEC check did not fail" )
    elif c.CBMC_RES_FAIL in res_str:
        l.warning( "DEC check failed" )
        return u.Status( False, 'CBMC_ASSERT' )
    else:
        l.error( "No result from cbmc, line is: {}".format( res_str ))
        return u.Status( False, 'CBMC_ERROR' )

    # Look at output for pos
    res_idx = ret.stdout.find( c.CBMC_POS_ASSERT )
    if res_idx == -1:
        l.error( "CBMC did not have result" )
        return u.Status( False, 'CBMC_ERROR' )
    line_end_idx = ret.stdout.find( '\n', res_idx )
    res_str = ret.stdout[ res_idx : line_end_idx ]
    if c.CBMC_RES_PASS in res_str:
        l.info( "POS check did not fail" )
    elif c.CBMC_RES_FAIL in res_str:
        l.warning( "POS check failed" )
        return u.Status( False, 'CBMC_ASSERT' )
    else:
        l.error( "No result from cbmc, line is: {}".format( res_str ))
        return u.Status( False, 'CBMC_ERROR' )

    # Some other error, report
    if ret.returncode != 0:
        l.error( 
            "Running cbmc failed with return code {} stdout {} stderr {}".format( 
                ret.returncode, ret.stdout, ret.stderr
        ))
        return u.Status( False, 'CBMC_ERROR' )

    return u.Status( True, None )


def validate( loop_data ):
    """ Perform validation steps. see validate_* methods above """

    if c.DO_TESTS:
        ret = validate_test( loop_data )
        if not ret.success:
            return ret

    if c.DO_CBMC:
        ret = validate_cbmc( loop_data )
        if not ret.success:
            return ret

    return u.Status( True, None )


if __name__ == '__main__':
    if c.DEBUG:

        u.init_logging()
        
        loop_data = u.LoopData(
            full_code="""






extern void abort(void);

extern void __assert_fail (const char *__assertion, const char *__file,
      unsigned int __line, const char *__function)
     __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));
extern void __assert_perror_fail (int __errnum, const char *__file,
      unsigned int __line, const char *__function)
     __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));
extern void __assert (const char *__assertion, const char *__file, int __line)
     __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));

void reach_error() { ((void) sizeof ((0) ? 1 : 0), __extension__ ({ if (0) ; else __assert_fail ("0", "simple_array_index_value_1-2.c", 7, __extension__ __PRETTY_FUNCTION__); })); }
extern void abort(void);
void assume_abort_if_not(int cond) {
  if(!cond) {abort();}
}
void __VERIFIER_assert(int cond)
{
  if (!(cond)) {
    ERROR: {reach_error();abort();}
  }
  return;
}

unsigned int __VERIFIER_nondet_uint();

int main()
{
  unsigned int array[10000];
  unsigned int index = 0;
  unsigned int tmp = 0;

  while (1) {
    index = __VERIFIER_nondet_uint();
    if (index >= 10000) {
      break;
    }
    array[index] = index;
    tmp = index;
  }

  __VERIFIER_assert(tmp < 10000 && array[tmp] == tmp);


}
            """, 
            loop_code = """while (1) {
    index = __VERIFIER_nondet_uint();
    if (index >= 10000) {
      break;
    }
    array[index] = index;
    tmp = index;
  }""",
            loop_id=' 0 ', 
            loop_type='WhileStmt', 
            beg_line='26', 
            end_line='26', 
            variant='10000 - index', 
            invariant='0 <= index AND index <= 10000', 
            assigns='index',
        )

        validate( loop_data ) 
