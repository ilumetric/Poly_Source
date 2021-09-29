# Shader Uniform
vs_uni = '''
    uniform mat4 view_mat;
    uniform float Z_Bias;
    uniform float Z_Offset;

    vec4 pos_view;
    
    in vec3 pos;
    in vec3 nrm;



    void main()
    {
        pos_view = view_mat * vec4(pos+(nrm*Z_Offset), 1.0f);
        pos_view.z = pos_view.z - Z_Bias / pos_view.z; 
        gl_Position = pos_view;
    }
'''

fs_uni = '''
    uniform vec4 color;
    out vec4 fragColor;

    void main()
    {
        fragColor = vec4(color.xyz, color.w);
    }

'''
 


# Shader Smooth
vs_sm = '''
    uniform mat4 view_mat;
    uniform float Z_Bias;
    uniform float Z_Offset;


    vec4 pos_view;
    
    in vec3 pos;
    in vec3 nrm;
    in vec4 col;

    out vec4 color;

    void main()
    {
        pos_view = view_mat * vec4(pos+(nrm*Z_Offset), 1.0f);
        color = col;
        pos_view.z = pos_view.z - Z_Bias / pos_view.z; 
        gl_Position = pos_view;
    }
'''

fs_sm = '''
    in vec4 color;
    out vec4 fragColor;

    void main()
    {
        fragColor  = vec4(color.xyz, color.w);
    }
'''

