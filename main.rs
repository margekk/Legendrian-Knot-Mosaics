// ~~~~
/*
Rust function to iteratively generate and print all suitably connected n x n legendrian mosaics, along with a basic driver program.
The total number of suitably connected legendrian mosaics is then simply the line count of the resulting file.

See the associated python file for information on how these mosaics are catalogued

This material is based upon work supported by the National Science Foundation under Grant No. MPS-2150299
*/

use dialoguer::Input; //For driver function
use std::fs::File;
use std::io::{BufWriter, Write, Result};
use std::time::Instant;

/* 
Connection table for mosaic generation
Essentially a hash map, states of surrounding tiles are converted to a base-3 number,
 and the list of tiles at that index in CONNECTION_TABLE represents all tiles that would be suitably connected given these surroundings
 0: no connection to tile
 1: must connect to tile
 2: undecided, may or may not connect

 Digits in the number are assigned as below:
    1
 2 ▇▇ 0
    3
 e.g. 0201 would indicate that the tile:
 must connect to the tile to its right,
 mustn't connect to the tiles above/below it,
 may or may not connect to the tile to its left
*/
const CONNECTION_TABLE: &[&[usize]]= &[ 
    //000x
    &[0],        
    &[],
    &[0],
    //001x
    &[],       
    &[3],
    &[3],
    //002x
    &[0],        
    &[3],
    &[0,3],
    //010x
    &[],        
    &[5],
    &[5],
    //011x
    &[4],       
    &[],
    &[4],
    //012x
    &[4],        
    &[5],
    &[4,5],
    //020x
    &[0],        
    &[5],
    &[0,5],
    //021x
    &[4],       
    &[3],
    &[3,4],
    //022x
    &[0,4],        
    &[3,5],
    &[0,3,4,5],
    //100x
    &[],        
    &[2],
    &[2],
    //101x
    &[6],       
    &[],
    &[6],
    //102x
    &[6],        
    &[2],
    &[2,6],
    //110x
    &[1],        
    &[],
    &[1],
    //111x
    &[],       
    &[7,8,9],
    &[7,8,9],
    //112x
    &[1],        
    &[7,8,9],
    &[1,7,8,9],
    //120x
    &[1],        
    &[2],
    &[1,2],
    //121x
    &[6],       
    &[7,8,9],
    &[6,7,8,9],
    //122x
    &[6],        
    &[2,7,8,9],
    &[2,6,7,8,9],
    //200x
    &[0],        
    &[2],
    &[0,2],
    //201x
    &[6],       
    &[3],
    &[3,6],
    //202x
    &[0,6],        
    &[2,3],
    &[0,2,3,6],
    //210x
    &[1],        
    &[5],
    &[1,5],
    //211x
    &[4],       
    &[7,8,9],
    &[4,7,8,9],
    //212x
    &[1,4],        
    &[5,7,8,9],
    &[1,5,7,8,9],
    //220x
    &[0,1],        
    &[2,5],
    &[0,1,2,5],
    //221x
    &[4,6],       
    &[3,7,8,9],
    &[3,4,5,7,8,9],
    //222x
    &[0,1,4,6],        
    &[2,3,5,7,8,9],
    &[0,1,2,3,4,5,6,7,8,9]
];

//Basic driver function
fn main() -> Result<()> {
    let size: usize = Input::new()
    .with_prompt("Size of generated mosaics?")
    .interact_text()
    .unwrap();  

    let output_path: String = Input::new()
    .with_prompt("Path to Write Generated Mosaics To?")
    .interact_text()
    .unwrap();   
    
    let now = Instant::now(); //Timing 
    mosaic_gen(&output_path, size)?;
    print!("Generation complete! ({:.6} s)", now.elapsed().as_secs_f64());

    Ok(())
}


/* Prints all size x size mosaics to a file at output_path
This function essentially just counts upwards -- each mosaic is represented by a base-10 number with size^2 digits, produced by reading the mosaic left to right, top to bottom.
e.g. 555020001 = 555
                 020
                 001
During generation, we keep a list of valid tiles for each digit based on the tiles leftward and above that digit in the underlying mosaic.
Whenever we have to "carry" a digit, we create new lists of valid tiles for every digit to the right of the carried digit
This guarantees that we produce every suitably connected size x size mosaic, which are written to a file as they're iterated through 
*/
fn mosaic_gen(output_path: &str, size: usize ) -> Result<()> {
    let vector_length = size*size - 1;
    let mut mosaic: Vec<usize> = vec![0; vector_length + 1];
    let mut curr_tile: usize = 0;
    let mut rightward = true;
    let mut digit_index: Vec<usize> = vec![0; vector_length + 1];
    let mut valid_tiles_for: Vec<&[usize]> = Vec::with_capacity(vector_length + 1);
    unsafe {
        valid_tiles_for.set_len(vector_length + 1);
    }

    let output_file: File = File::create(output_path)?;
    let mut output_buffer = BufWriter::new(output_file);

    loop {
        //Determining the list of valid tiles for the current tile based on tiles to top/left, and whether tile is on right/bottom edge of mosaic
        if rightward {
            valid_tiles_for[curr_tile] = CONNECTION_TABLE [
                if curr_tile%size == size - 1 {0} else {2} //right
                +3*( if curr_tile/size == 0 {0} else { //up
                    match mosaic[ curr_tile - size ] { 
                    0|3|4|5 => 0,
                    _ => 1
                    }
                })
                +9*( if curr_tile%size == 0 {0} else { //left
                    match mosaic[ curr_tile - 1 ] { 
                    0|1|4|6 => 0,
                    _ => 1
                    }
                })
                +27*(if curr_tile/size == size - 1 {0} else {2}) //down
            ];
            
            //Determining if there are no valid tiles based on the current configuration
            if valid_tiles_for[curr_tile].len() == 0 {
               rightward = false;
                curr_tile -= 1;
                continue;
            }

            //Setting the current tile to the first valid tile
            digit_index[curr_tile] = 1; //Note that digit index represents the index of the _next_ valid tile to be used for a given tile in the mosaic
            mosaic[curr_tile] = valid_tiles_for[curr_tile][0];
            
            //
            if curr_tile == vector_length {
                rightward = false;
                continue;
            }
            curr_tile += 1;
            continue;
        }

        if curr_tile == vector_length { //Writing complete mosaics
            writeln!(output_buffer, "{}", mosaic.iter().map(|val| format!("{}", val)).collect::<Vec<String>>().join(""))?;
        }

        //"Carrying" leftward when we've used every valid tile for the current tile
        if digit_index[curr_tile] == valid_tiles_for[curr_tile].len() {
            if curr_tile == 0 { //Ends the program
                break;
            }
            curr_tile -= 1;
            continue;
        }

        //Move to next tile in list of valid tiles
        mosaic[curr_tile] = valid_tiles_for[curr_tile][digit_index[curr_tile]];
        digit_index[curr_tile] += 1;
        if curr_tile < vector_length {
            curr_tile += 1;
            rightward = true;
        }
    }
    Ok(())
}