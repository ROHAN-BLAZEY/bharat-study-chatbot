import torch
import torch.nn as nn

class SimpleTransformerBlock(nn.Module):
    def __init__(self, embed_size, heads, forward_expansion):
        super(SimpleTransformerBlock, self).__init__()
        self.attention = nn.MultiheadAttention(embed_dim=embed_size, num_heads=heads)
        self.norm1 = nn.LayerNorm(embed_size)
        self.norm2 = nn.LayerNorm(embed_size)
        
        self.feed_forward = nn.Sequential(
            nn.Linear(embed_size, forward_expansion * embed_size),
            nn.ReLU(),
            nn.Linear(forward_expansion * embed_size, embed_size)
        )
        
    def forward(self, value, key, query):
        attention_out, _ = self.attention(query, key, value)
        x = self.norm1(attention_out + query)
        forward_out = self.feed_forward(x)
        out = self.norm2(forward_out + x)
        return out

print("Transformer Block Defined Successfully")
